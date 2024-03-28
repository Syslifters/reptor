import typing

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.models.Note import NoteTemplate
from reptor.models.UserConfig import UserConfig


class Nessus(ToolBase):
    meta = {
        "author": "Syslifters",
        "name": "Nessus",
        "version": "1.0",
        "license": "MIT",
        "tags": [],
        "summary": "Nessus vulnerability importer",
    }

    risk_mapping = {
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
        self.notetitle = kwargs.get("notetitle") or "Nessus"
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
                    "Invalid filter range. Use keywords from 'info,low,medium,high,critical'"
                )
            filter_elements = list()
            for i in range(min(filter_indexes), max(filter_indexes) + 1):
                filter_elements += [list(self.risk_mapping.keys())[i]]
        elif filter:
            filter_elements = filter.split(",")
            if not all(f in self.risk_mapping for f in filter_elements):
                raise ValueError(
                    "Invalid filter. Use keywords from 'info,low,medium,high,critical'"
                )
        if filter_elements:
            return set(filter_elements)
        else:
            return set(self.risk_mapping.keys())

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
        data = self.parsed_input
        # Create note structure
        ## Main note
        main_note = NoteTemplate()
        main_note.title = self.notetitle
        main_note.icon_emoji = self.note_icon

        ## Subnotes per target
        for host in data:
            host_overview = NoteTemplate()
            host_overview.title = f"{host['target']}"
            host_overview.checked = False
            host_overview.template = "nessus-host-overview"
            host_overview.template_data = host
            for finding in host["findings"]:
                finding_note = NoteTemplate()
                finding_note.title = f"{ self.risk_mapping.get(finding.get('risk_factor', 'info').lower()) } {finding['plugin_name']}"
                finding_note.checked = False
                finding_note.template = "nessus-finding"
                finding_note.template_data = finding
                finding_note.force_new = True
                host_overview.children.append(finding_note)
            main_note.children.append(host_overview)
        if not main_note.children:
            return None
        return main_note

    def parse(self):
        super().parse()
        p = list()
        if isinstance(self.parsed_input, list):
            p = self.parsed_input[0].get("NessusClientData_v2", dict())
            p = p.get("Report", dict()).get("ReportHost", list())
            if not isinstance(p, list):
                p = [p]
            for i in range(1, len(self.parsed_input)):
                report_host = (
                    self.parsed_input[i]
                    .get("NessusClientData_v2", dict())
                    .get("Report", dict())
                    .get("ReportHost", list())
                )
                if not isinstance(report_host, list):
                    report_host = [report_host]
                p += report_host
        elif self.parsed_input:
            p = (
                self.parsed_input.get("NessusClientData_v2", dict())
                .get("Report", dict())
                .get("ReportHost", list())
            )
            if not isinstance(p, list):
                p = [p]

        hosts = list()
        for host in p:
            host_data = dict()
            # Get tags from HostProperties
            for tag in host.get("HostProperties", dict()).get("tag", list()):
                key = tag.get("@name", "").replace("-", "_").replace("@", "")
                v = tag.get("#text", "")
                host_data[key] = v
            # Apply filter
            # Get hostname
            host_data["target"] = host.get("@name", "")
            # Get findings
            findings = host.get("ReportItem", list())
            if not isinstance(findings, list):
                findings = [findings]
            if self.included_plugins:
                findings = [
                    f for f in findings if f.get("@pluginID") in self.included_plugins
                ]
            if self.excluded_plugins:
                findings = [
                    f
                    for f in findings
                    if f.get("@pluginID") not in self.excluded_plugins
                ]
            for f in findings:
                if f.get("risk_factor", "").lower() == "none":
                    f["risk_factor"] = "Info"
            host_data["findings"] = [
                f
                for f in findings
                if f.get("risk_factor", "info").lower() in self.severity_filter
            ]
            if not host_data["findings"]:
                continue
            for finding in host_data["findings"]:
                if "see_also" in finding and not isinstance(finding["see_also"], list):
                    finding["see_also"] = [finding["see_also"]]
                for key in list(finding.keys()):
                    finding[key.replace("@", "")] = finding.pop(key)

            host_data["findings"] = sorted(
                host_data["findings"],
                key=lambda x: int(x.get("severity", 0)),
                reverse=True,
            )
            hosts.append(host_data)

        # Order hosts by highest finding @severity
        self.parsed_input = sorted(
            hosts, key=lambda x: int(x["findings"][0].get("severity", 0)), reverse=True
        )

    def aggregate_findings(self) -> dict:
        """
        Aggregates findings by pluginID
        """
        findings = dict()
        for host in self.parsed_input:
            for finding in host["findings"]:
                finding["host_ip"] = host["host_ip"]
                finding["target"] = host["target"]
                findings.setdefault(finding["pluginID"], list()).append(finding)
        for plugin_findings in findings.values():
            aggregated_finding = dict()
            for plugin_finding in plugin_findings:
                target = plugin_finding.get("target") or plugin_finding.get("host_ip") or "n/a"
                port = plugin_finding.get("port") or "0"
                svc_name = plugin_finding.get("svc_name") or "general"
                plugin_finding["affected_components"] = (
                    f"{target}{':' + port if port != '0' else ''}{' (' + svc_name + ')' if svc_name != 'general' else ''}"
                )

                for key, value in plugin_finding.items():
                    if key in [
                        "risk_factor",
                        "severity",
                        "cvss_vector",
                        "cvss_base_score",
                        "cvss_temporal_vector",
                        "cvss_temporal_score",
                    ]:
                        if float(aggregated_finding.get("severity", 0)) <= float(
                            plugin_finding.get("severity", 0)
                        ):
                            aggregated_finding[key] = value
                        continue
                    if key == "see_also":
                        if not value:
                            value = list()
                        value = list(set(aggregated_finding.get(key, list()) + value))
                    elif key in [
                        "plugin_output",
                        "port",
                        "protocol",
                        "svc_name",
                        "target",
                        "host_ip",
                        "affected_components",
                    ]:
                        value = aggregated_finding.get(key, list()) + [value]
                    aggregated_finding[key] = value

            findings[plugin_finding["pluginID"]] = aggregated_finding
        return findings

    def preprocess_for_template(self) -> list:
        findings = self.aggregate_findings()
        for finding in findings.values():
            finding["affected_components"] = sorted(set(finding["affected_components"]))
            if cvss := finding.get("cvss_vector"):
                finding["cvss_vector"] = self.cvss2_to_3(cvss)

            finding["risk_factor"] = finding.get("risk_factor", "").lower()
            if finding["risk_factor"] not in self.risk_mapping:
                finding["risk_factor"] = "info"
            finding["severity_figure"] = finding["severity"]
            finding["severity"] = finding["risk_factor"]  # Provide for enum
            finding["finding_templates"] = finding["pluginID"]

        return list(findings.values())

    def finding_global(self):
        return self.preprocess_for_template()


loader = Nessus
