import re
import typing
from copy import deepcopy

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.models.Note import NoteTemplate
from reptor.models.UserConfig import UserConfig


class Burp(ToolBase):
    meta = {
        "author": "Syslifters",
        "name": "Burp",
        "version": "1.0",
        "license": "MIT",
        "tags": [],
        "summary": "Burp vulnerability importer",
    }

    risk_mapping = {
        "info": "🟢",
        "low": "🔵",
        "medium": "🟡",
        "high": "🟠",
    }
    group_fields = ["serialNumber", "host", "path", "location", "collaboratorEvent"]
    remove_fields = ["requestresponse"]
    supports_multi_input = True  # TODO

    def _parse_severity_filter(self, filter: str) -> set:
        if filter is None:
            return set(self.risk_mapping.keys())
        filter_elements = set()
        if "-" in filter:
            filter_elements = filter.split("-")
            try:
                filter_indexes = [
                    list(self.risk_mapping.keys()).index(f) for f in filter_elements
                ]
            except ValueError:
                raise ValueError(
                    "Invalid filter range. Use keywords from 'info,low,medium,high'"
                )
            filter_elements = list()
            for i in range(min(filter_indexes), max(filter_indexes) + 1):
                filter_elements += [list(self.risk_mapping.keys())[i]]
        elif filter:
            filter_elements = filter.split(",")
            if not all(f in self.risk_mapping for f in filter_elements):
                raise ValueError(
                    "Invalid filter. Use keywords from 'info,low,medium,high'"
                )
        if filter_elements:
            return set(filter_elements)
        else:
            return set(self.risk_mapping.keys())

    @property
    def user_config(self) -> typing.List[UserConfig]:
        return [
            UserConfig(
                name="severity_filter",
                friendly_name='Severity filter (e.g., "medium-high")',
                callback=self._parse_severity_filter,
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
        self.notetitle = kwargs.get("notetitle") or "Burp"
        self.note_icon = "🟧"
        self.input_format = "xml"
        self.timestamp = False
        self.severity_filter = getattr(
            self, "severity_filter", None
        ) or self._parse_severity_filter(kwargs.get("severity_filter", "info-high"))
        self.included_plugins = getattr(self, "included_plugins", list())
        self.included_plugins += list(
            filter(None, ((kwargs.get("included_plugins")) or "").split(","))
        )
        self.excluded_plugins = getattr(self, "excluded_plugins", list())
        self.excluded_plugins += list(
            filter(None, ((kwargs.get("excluded_plugins")) or "").split(","))
        )

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--severity-filter",
            help='Filter findings by severity comma-separated ("info,low,medium,high") or as range ("medium-high")',
            action="store",
            dest="severity_filter",
            default=None,
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
        # Create note structure
        ## Main note
        main_note = NoteTemplate()
        main_note.title = self.notetitle
        main_note.icon_emoji = self.note_icon

        ## Subnotes per target
        for ip, findings in self.aggregate_by_ip().items():
            host_overview = NoteTemplate()
            host_overview.title = ip
            host_overview.checked = False
            host_overview.template = "burp-host-overview"
            host_overview.template_data = {"findings": findings, "ip": ip}
            for finding in findings:
                finding_note = NoteTemplate()
                finding_note.title = f"{ self.risk_mapping.get(finding.get('severity', 'info').lower()) } {finding['name']}"
                finding_note.checked = False
                finding_note.template = "burp-finding"
                finding_note.template_data = finding
                finding_note.force_new = True
                host_overview.children.append(finding_note)
            main_note.children.append(host_overview)
        if not main_note.children:
            return None
        return main_note

    def parse(self):
        super().parse()
        if not self.parsed_input:
            self.display("No data to parse.")
            return
        if isinstance(self.parsed_input, dict):
            self.parsed_input = [self.parsed_input]
        elif not isinstance(self.parsed_input, list):
            self.warning("Cannot handle this format. Expected dict input.")
            return

        findings = [finding for input in self.parsed_input for finding in input.get("issues", {}).get("issue", [])]

        # Exclude False Positives
        findings = [f for f in findings if f.get("severity") != "False Positive"]

        # Normalize severity
        for finding in findings:
            finding["severity"] = (finding.get("severity") or "info").lower()
            if finding["severity"] == "information":
                finding["severity"] = "info"

        # Apply filters
        if self.included_plugins:
            findings = [f for f in findings if f.get("type") in self.included_plugins]
        if self.excluded_plugins:
            findings = [
                f for f in findings if f.get("type") not in self.excluded_plugins
            ]
        if self.severity_filter:
            if any(f not in self.risk_mapping for f in self.severity_filter):
                raise ValueError(
                    f"Invalid severity filter. Use keywords from {', '.join(self.risk_mapping.keys())}"
                )
            findings = [
                f
                for f in findings
                if (f.get("severity") or "").lower() in self.severity_filter
            ]

        # References to list
        for finding in findings:
            finding["references"] = re.findall(
                r"<a\s+href=['\"](.*?)['\"]", finding.get("references") or ""
            )

        # Set severity score
        for finding in findings:
            finding["severity_score"] = list(self.risk_mapping.keys()).index(
                finding["severity"]
            )

        # Order by severity score
        self.parsed_input = sorted(
            findings, key=lambda x: x.get("severity_score", 0), reverse=True
        )

    def _remove_fields(self, finding: dict) -> dict:
        for field in self.remove_fields:
            finding.pop(field, None)
        return finding

    def _group_findings(self, findings: list) -> typing.Optional[dict]:
        if not findings:
            return None
        for field in self.group_fields:
            values = list()
            for finding in findings:
                if value := finding.get(field):
                    values.append(value)
            if values:
                findings[0][field] = values
        self._remove_fields(findings[0])
        return findings[0]

    def aggregate_by_ip(self) -> dict:
        finding_groups = dict()
        for finding in deepcopy(self.parsed_input) or list():
            if host := finding.get("host"):
                ip = host.get("@ip") or host.get("#text") or "_"
            else:
                ip = "_"
            finding_groups.setdefault(ip, list()).append(finding)

        for ip, findings in finding_groups.items():
            if ip != "_":
                finding_groups[ip] = self.merge_findings_by_type(findings)
        return finding_groups

    def merge_findings_by_type(self, findings) -> list:
        result = list()
        finding_groups = dict()
        for finding in deepcopy(findings) or list():
            if not (type := finding.get("type")):
                result.append(finding)
                continue
            finding_groups.setdefault(type, list()).append(finding)

        for type, findings in finding_groups.items():
            if not findings:
                continue
            # Create affected_components
            affected_components = list()
            for finding in findings:
                if not (host := finding.get("host")):
                    continue
                url = host.get("#text") or host.get("@ip")
                ip = host.get("@ip")
                location = finding.get("location") or finding.get("path") or ""
                affected_components.append(
                    f"{url or ip}{location}{f' ({ip})' if ip and url else ''}"
                )
            findings[0]["affected_components"] = affected_components

            # Add finding template information
            findings[0]["finding_templates"] = type

            # Group and append to aggregated findings
            result.append(self._group_findings(findings))

        # Order by severity score
        return sorted(result, key=lambda x: x.get("severity_score", 0), reverse=True)

    def preprocess_for_template(self) -> list:
        return self.merge_findings_by_type(self.parsed_input)

    def finding_global(self):
        return self.preprocess_for_template()


loader = Burp
