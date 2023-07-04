import typing

from xml.etree import ElementTree

from core.modules.ToolBase import ToolBase

from modules.OWASPZap.models import Site, Alert, Instance


class OWASPZap(ToolBase):
    """
    Parses OWASPZap XML and JSON reports
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = "OWASP Zap"
        self.arg_type_json = kwargs.get("json")
        self.arg_type_xml = kwargs.get("xml")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        simplelist_parser = parser.add_mutually_exclusive_group()
        simplelist_parser.add_argument(
            "--json", help="Loads JSON File", action="store_true", default=False
        )
        simplelist_parser.add_argument(
            "--xml", help="Loads JSON File", action="store_true", default=False
        )

        """Todo:
        - Create toggle for instance include or not
        - Create fields inclusion by list i.e --fields=description,solution,references
        - Create blacklist i.e --blacklist=risk,confidence
        """

    def parse_json(self, data) -> typing.List[Site]:
        raise NotImplementedError

    def parse_xml(self, data) -> typing.List[Site]:
        root = ElementTree.fromstring(data)
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

        return return_data

    def parse(self):
        super().parse()
        parsed_input = list()
        if self.arg_type_json:
            parsed_input = self.parse_json(self.raw_input)
        elif self.arg_type_xml:
            parsed_input = self.parse_xml(self.raw_input)

        self.parsed_input = parsed_input

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
