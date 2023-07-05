import typing

from xml.etree import ElementTree

from core.modules.ToolBase import ToolBase

from modules.OWASPZap.models import Site, Alert, Instance


class OWASPZap(ToolBase):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: owasp, zap

    Short Help:
    Parses OWASPZap XML and JSON reports

    Description:
    Parses OWASPZap generated reports in either XML or JSON

    Make sure you verify what type of findings you export.

    Recommended settings are to only export Medium and higher findings
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = "OWASP Zap"

    def parse_json(self, data):
        raise NotImplementedError

    def parse_xml(self, root):
        return_data = list()
        for owasp_scan in root:
            site = Site()
            site.parse(owasp_scan)

            for alert_item in owasp_scan[0]:
                alert = Alert()
                alert.parse(alert_item)

                for instance_item in alert_item.findall("./instances/instance"):
                    instance = Instance()
                    instance.parse(instance_item)
                    alert.instances.append(instance)

                site.alerts.append(alert)

            return_data.append(site)

        self.parsed_input = return_data

    def format(self):
        super().format()

        output = list()

        owasp_scan_sites: typing.List[Site] = self.parsed_input

        for site in owasp_scan_sites:
            site_output = f"""

            # OWASPZap Scan

            ## Site Details
            | Target | Information |
            | :--- | :--- |
            | Site | {site.name} |
            | Host | {site.host} |
            | Port | {site.port} |
            | SSL ? | {'Yes' if site.ssl.lower().startswith("t") else 'No'} |

            ## Alerts
            """

            output.append(site_output)

            for alert in site.alerts:
                alert_output = f"""

                ### {alert.name}
                | Target | Information |
                | :--- | :--- |
                | Risk | {alert.riskdesc} |
                | Confidence | {alert.confidencedesc} |
                | Number of Affected Instances | {alert.count} |
                | CWE | [{alert.cweid}](https://cwe.mitre.org/data/definitions/{alert.cweid}.html) |

                ### Description
                {alert.desc}

                ### Solution
                {alert.solution}

                ### References
                """

                if alert.reference:
                    for reference in alert.reference.splitlines():
                        alert_output += f"""
                        - [{reference}]({reference})
                """
                else:
                    alert_output += "None"

                output.append(alert_output)

        self.formatted_input = "\n".join(output)


loader = OWASPZap
