import typing

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.models.Note import NoteTemplate
from reptor.models.UserConfig import UserConfig


class OpenVAS(ToolBase):
    meta = {
        "author": "Syslifters",
        "name": "OpenVAS",
        "version": "1.0",
        "license": "MIT",
        "tags": [],
        "summary": "OpenVAS vulnerability importer",
    }

    score_mapping = {
        0: "info",
        3.9: "low",
        6.9: "medium",
        8.9: "high",
        10: "critical",
    }
    severity_mapping = {
        "info": "🟢",
        "low": "🔵",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴",
    }
    supports_multi_input = True

    @property
    def user_config(self) -> typing.List[UserConfig]:
        return [
            UserConfig(
                name="severity_filter",
                friendly_name='Severity filter (e.g., "medium-critical")',
                callback=self._parse_severity_filter,
            ),
            UserConfig(
                name="min_qod",
                friendly_name="Minimum QoD (0-100)",
                callback=int,
            ),
            UserConfig(
                name="excluded_plugins",
                friendly_name="Exclude plugin IDs (comma-separated)",
                callback=UserConfig.split,
            ),
            UserConfig(
                name="included_plugins",
                friendly_name="Include plugin IDs (comma-separated)",
                callback=UserConfig.split,
            ),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notetitle = kwargs.get("notetitle") or "OpenVAS"
        self.note_icon = "🦖"
        self.input_format = "xml"
        self.timestamp = False
        self.severity_filter = getattr(
            self, "severity_filter", None
        ) or self._parse_severity_filter(kwargs.get("severity_filter", "low-critical"))
        self.min_qod = getattr(self, "min_qod", None) or kwargs.get("min_qod", 0)

        self.included_plugins = getattr(self, "included_plugins", list())
        self.included_plugins += list(
            filter(None, ((kwargs.get("included_plugins")) or "").split(","))
        )
        self.excluded_plugins = getattr(self, "excluded_plugins", list())
        self.excluded_plugins += list(
            filter(None, ((kwargs.get("excluded_plugins")) or "").split(","))
        )

    def _parse_severity_filter(self, filter: str) -> set:
        if filter is None:
            return set(self.severity_mapping.keys())
        filter_elements = set()
        if "-" in filter:
            filter_elements = filter.split("-")
            try:
                filter_indexes = [
                    list(self.severity_mapping.keys()).index(f) for f in filter_elements
                ]
            except ValueError:
                raise ValueError(
                    "Invalid filter range. Use keywords from 'info,low,medium,high,critical'"
                )
            filter_elements = list()
            for i in range(min(filter_indexes), max(filter_indexes) + 1):
                filter_elements += [list(self.severity_mapping.keys())[i]]
        elif filter:
            filter_elements = filter.split(",")
            if not all(f in self.severity_mapping for f in filter_elements):
                raise ValueError(
                    "Invalid filter. Use keywords from 'info,low,medium,high,critical'"
                )
        if filter_elements:
            return set(filter_elements)
        else:
            return set(self.severity_mapping.keys())

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--severity-filter",
            help='Filter findings by severity comma-separated ("high,medium") or as range ("medium-critical")',
            action="store",
            dest="severity_filter",
            default=None,
        )
        parser.add_argument(
            "--min-qod",
            help="Minimum OpenVAS Quality of Detection (QoD) to include (0-100)",
            action="store",
            type=int,
            dest="min_qod",
            default=0,
        )
        parser.add_argument(
            "--exclude",
            help="Exclude plugin IDs, comma-separated",
            action="store",
            dest="excluded_plugins",
            default=None,
        )
        parser.add_argument(
            "--include",
            help="Include plugin IDs, comma-separated; default: all are included",
            action="store",
            dest="included_plugins",
            default=None,
        )

    def create_notes(self):
        self.parse()
        data = self.aggregate_by_target()
        # Create note structure
        ## Main note
        main_note = NoteTemplate()
        main_note.title = self.notetitle
        main_note.icon_emoji = self.note_icon

        ## Subnotes per target
        for findings in data:
            host_overview = NoteTemplate()
            host_overview.title = f"{findings[0]['target']}"
            host_overview.checked = False
            host_overview.template = "host-overview"
            host_overview.template_data = {"data": findings}
            for f in findings:
                finding_note = NoteTemplate()
                finding_note.title = f"{ self.severity_mapping.get(f.get('risk_factor', 'info').lower()) } {f['name']}"
                finding_note.checked = False
                finding_note.template = "finding"
                finding_note.template_data = f
                finding_note.force_new = True
                host_overview.children.append(finding_note)
            main_note.children.append(host_overview)
        if not main_note.children:
            return None
        return main_note

    def _get_findings(self, input) -> list:
        if "get_reports_response" in input:
            input = input["get_reports_response"]
        results = input.get("report", dict())
        if results.get("report_format", dict()).get("name") == "Anonymous XML":
            self.log.warning("Anonymous XML. You might want to export as XML instead.")
        return (
            results.get("report", dict()).get("results", dict()).get("result", list())
        )

    def parse(self):
        super().parse()
        if not self.parsed_input:
            return
        if isinstance(self.parsed_input, list):
            # Multiple input files. Merge findings
            findings = self._get_findings(self.parsed_input[0])
            for i in range(1, len(self.parsed_input)):
                findings += self._get_findings(self.parsed_input[i])
        else:
            findings = self._get_findings(self.parsed_input)

        # Filter severity and plugins
        filtered = list()
        for finding in findings:
            finding["severity"] = float(finding.get("severity", "0"))
            for score_threshold, risk_factor in self.score_mapping.items():
                if finding["severity"] <= score_threshold:
                    finding["risk_factor"] = risk_factor
                    try:
                        finding["nvt"]["oid"] = finding["nvt"].pop("@oid")
                    except (KeyError, AttributeError):
                        finding["nvt"]["oid"] = ""
                    if risk_factor in self.severity_filter:
                        filtered.append(finding)
                    break

        findings = [
            f
            for f in filtered
            if self.min_qod <= int(f.get("qod", dict()).get("value", "0"))
        ]
        if self.included_plugins:
            findings = [
                f
                for f in findings
                if f.get("nvt", dict()).get("oid") in self.included_plugins
            ]
        if self.excluded_plugins:
            findings = [
                f
                for f in findings
                if f.get("nvt", dict()).get("oid") not in self.excluded_plugins
            ]

        for f in findings:
            # Parse nvt tags
            tags = f.get("nvt", dict()).get("tags", "")
            tags = {i[0]: i[1] for i in (item.split("=") for item in tags.split("|"))}
            f["nvt"]["tags"] = tags

            # Get target name
            f["target"] = f.get("host", dict()).get("hostname") or f.get(
                "host", dict()
            ).get("#text", "")
            try:
                f["host"]["ip"] = f["host"].pop("#text")
            except (KeyError, AttributeError):
                f["host"]["ip"] = ""

        # Sort
        findings = sorted(
            findings,
            key=lambda x: (x.get("severity", 0), x.get("name", "")),
            reverse=True,
        )
        self.parsed_input = findings

    def aggregate_by_target(self) -> list:
        targets = dict()
        for finding in self.parsed_input:
            targets.setdefault(finding["target"], list()).append(finding)

        # Sort hosts by highest severity
        targets = list(targets.values())
        targets.sort(
            key=lambda x: (x[0].get("severity", 0), x[0].get("name", "")), reverse=True
        )
        return targets

    def aggregate_by_plugin(self) -> list:
        plugins = dict()
        for finding in self.parsed_input:
            plugins.setdefault(
                finding.get("nvt", dict()).get("oid", ""), list()
            ).append(finding)

        # Sort by highest severity
        plugins = list(plugins.values())
        plugins.sort(
            key=lambda x: (x[0].get("severity", 0), x[0].get("name", "")), reverse=True
        )
        return plugins

    @classmethod
    def merge_findings(cls, findings: list) -> dict:
        m = dict()
        if not findings:
            return m
        for finding in findings:
            for k, v in finding.get("nvt", dict()).get("tags", dict()).items():
                m.setdefault(k, v)
            if "cvss_base_vector" in m:
                m.setdefault("cvss_vector", cls.cvss2_to_3(m["cvss_base_vector"]))
            if "name" in finding.keys():
                m.setdefault("name", finding["name"])
            if "description" in finding.keys():
                m.setdefault("description", list()).append(finding["description"])
            if "oid" in finding.get("nvt", dict()).keys():
                m.setdefault("oid", finding["nvt"]["oid"])
            if "risk_factor" in finding.keys():
                m.setdefault("risk_factor", finding["risk_factor"].lower())
            if "refs" in finding.get("nvt", dict()).keys():
                m.setdefault("refs", list())
                refs = finding["nvt"]["refs"].get("ref", dict)
                if isinstance(refs, dict):
                    refs = [refs]
                for ref in refs:
                    m["refs"].append(ref.get("@id", ""))
                m["refs"] = sorted(set(m["refs"]))
            m.setdefault("affected_components", list()).append(
                f"{finding['target']}{':' + finding['port'] if not finding['port'].startswith('general') else ''}"
            )
        m["affected_components"] = sorted(set(m["affected_components"]))
        return m

    def preprocess_for_template(self) -> list:
        plugin_findings = self.aggregate_by_plugin()
        findings = list()
        for plugin in plugin_findings:
            merged = self.merge_findings(plugin)
            merged["severity"] = merged["risk_factor"]
            merged["finding_templates"] = merged["oid"]
            findings.append(merged)
        return findings

    def finding_global(self):
        return self.preprocess_for_template()


loader = OpenVAS
