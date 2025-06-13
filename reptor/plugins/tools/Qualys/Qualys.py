import argparse
import typing
from urllib.parse import urlparse

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.models.Note import NoteTemplate
from reptor.models.UserConfig import UserConfig


class Qualys(ToolBase):
    meta = {
        "author": "Syslifters",
        "name": "Qualys",
        "version": "1.0",
        "license": "MIT",
        "tags": [],
        "summary": "Qualys vulnerability importer",
    }

    score_mapping = {
        1: "info",
        2: "low",
        3: "medium",
        4: "high",
        5: "critical",
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
                name="excluded_plugins",
                friendly_name="Exclude plugin QIDs (comma-separated)",
                callback=UserConfig.split,
            ),
            UserConfig(
                name="included_plugins",
                friendly_name="Include plugin QIDs (comma-separated)",
                callback=UserConfig.split,
            ),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notetitle = kwargs.get("notetitle") or "Qualys"
        self.note_icon = "🛡️"
        self.input_format = "xml"
        self.timestamp = False
        self.severity_filter = getattr(
            self, "severity_filter", None
        ) or self._parse_severity_filter(kwargs.get("severity_filter", "info-critical"))

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
            "--severityfilter",
            help=argparse.SUPPRESS,
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
                finding_note.title = f"{ self.severity_mapping.get(f.get('severity_label', 'info').lower()) } {f['TITLE']}"
                finding_note.checked = False
                finding_note.template = "finding"
                finding_note.template_data = f
                finding_note.force_new = True
                host_overview.children.append(finding_note)
            main_note.children.append(host_overview)
        if not main_note.children:
            return None
        return main_note

    def _get_findings_was(self, input) -> list:
        """
        Get findings from Web Application Scan report.
        """
        vulnerabilities = (
            input.get("WAS_SCAN_REPORT", dict())
            .get("RESULTS", dict())
            .get("VULNERABILITY_LIST")
            .get("VULNERABILITY", list())
        )
        glossary = (
            input.get("WAS_SCAN_REPORT", dict())
            .get("GLOSSARY", dict())
            .get("QID_LIST", dict())
            .get("QID", list())
        )
        glossary = {g["QID"]: g for g in glossary}
        for vulnerability in vulnerabilities:
            vulnerability.update(glossary.get(vulnerability.get("QID", ""), {}))
        return vulnerabilities

    def _get_findings_scan(self, input) -> list:
        findings = list()
        ips = input.get("SCAN", dict()).get("IP", list())
        if not isinstance(ips, list):
            ips = [ips]
        for ip in ips:
            vulns = ip.get("VULNS", list())
            if not isinstance(vulns, list):
                vulns = [vulns]
            for vuln in vulns:
                cats = vuln.get("CAT", list())
                if not isinstance(cats, list):
                    cats = [cats]
                for cat in cats:
                    finding = cat.get("VULN", dict())
                    # Remove special characters from field names
                    finding["CVEID"] = finding.pop("@cveid", "")

                    # Rename fields to match WAS format
                    finding["SEVERITY"] = finding.pop("@severity", "1")
                    finding["QID"] = finding.pop("@number", "")
                    finding["IMPACT"] = finding.pop("DIAGNOSIS", "")
                    finding["DESCRIPTION"] = finding.pop("CONSEQUENCE", "")
                    
                    # Add additional fields
                    finding["IP"] = ip.get("@value", "")

                    # Append to findings
                    findings.append(finding)
        return findings     

    def _get_findings(self, input) -> list:
        if "WAS_SCAN_REPORT" in input:
            return self._get_findings_was(input)
        elif "SCAN" in input:
            return self._get_findings_scan(input)
        else:
            raise NotImplementedError("This report type is not supported yet. Please open an issue at https://github.com/Syslifters/reptor/issues and provide a sample report.")

    def parse(self):
        super().parse()
        if not self.parsed_input:
            return
        if isinstance(self.parsed_input, list):
            # Multiple input files. Merge findings
            findings = []
            for input_file in self.parsed_input:
                findings.extend(self._get_findings(input_file))
        else:
            findings = self._get_findings(self.parsed_input)

        # Filter severity and plugins
        filtered = list()
        for finding in findings:
            for score_threshold, severity_label in self.score_mapping.items():
                if int(finding["SEVERITY"]) <= score_threshold:
                    finding["severity_label"] = severity_label
                    if severity_label in self.severity_filter:
                        filtered.append(finding)
                    break
        findings = filtered

        if self.included_plugins:
            findings = [ f for f in findings if f.get("QID", "") in self.included_plugins ]
        if self.excluded_plugins:
            findings = [ f for f in findings if f.get("QID", "") not in self.excluded_plugins ]

        # Sort
        findings = sorted(
            findings,
            key=lambda x: (int(x.get("SEVERITY", 0)), x.get("name", "")),
            reverse=True,
        )
        self.parsed_input = findings

    def aggregate_by_target(self) -> list:
        targets = dict()
        for finding in self.parsed_input:
            url = finding.get("IP") or finding.get("URL", "")
            finding["target"] = urlparse(url).netloc or finding.get("IP") or finding.get("URL") or "Unknown"
            targets.setdefault(finding["target"], list()).append(finding)

        # Sort hosts by highest severity
        targets = list(targets.values())
        targets.sort(
            key=lambda x: (int(x[0].get("SEVERITY", 0)), x[0].get("name", "")), reverse=True
        )
        return targets

    def aggregate_by_plugin(self) -> list:
        plugins = dict()
        for finding in self.parsed_input:
            plugins.setdefault(finding.get("QID", ""), list()).append(finding)

        # Sort by highest severity
        plugins = list(plugins.values())
        plugins.sort(
            key=lambda x: (int(x[0].get("severity", 0)), x[0].get("name", "")), reverse=True
        )
        return plugins

    @classmethod
    def merge_findings(cls, findings: list) -> dict:
        if not findings:
            return dict()
        m = findings[0].copy()
        for finding in findings:
            if url := finding.get('URL'):
                m.setdefault("URLS", list()).append(url)
            if param := finding.get('PARAM'):
                m.setdefault("PARAMS", list()).append(param)
            if access_path := finding.get('ACCESS_PATH'):
                m.setdefault("ACCESS_PATHS", list()).append(access_path)
            if ip := finding.get('IP'):
                m.setdefault("IPS", list()).append(ip)

        m["affected_components"] = sorted(set(m.get("URLS") or m.get("IPS") or []))
        return m

    def preprocess_for_template(self) -> list:
        plugin_findings = self.aggregate_by_plugin()
        findings = list()
        for plugin in plugin_findings:
            merged = self.merge_findings(plugin)
            merged["finding_templates"] = merged["QID"]
            findings.append(merged)
        return findings

    def finding_global(self):
        return self.preprocess_for_template()


loader = Qualys
