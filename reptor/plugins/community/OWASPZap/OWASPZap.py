from reptor.lib.plugins.ToolBase import ToolBase
from reptor.plugins.community.OWASPZap.models import Alert, Instance, Site


class OWASPZap(ToolBase):
    """
    Parses OWASPZap generated reports in either XML or JSON

    Make sure you verify what type of findings you export.

    Recommended settings are to only export Medium and higher findings
    """

    meta = {
        "author": "Richard Schwabe",
        "name": "OWASPZap",
        "version": "1.0",
        "license": "MIT",
        "tags": ["web", "owasp", "zap"],
        "summary": "Parses OWASPZap reports (JSON, XML)",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = kwargs.get("notename", "OWASP Zap")
        self.multi_notes = True
        self.note_icon = "🌩️"
        if self.input_format == "raw":
            self.input_format = "json"

    def parse_xml(self):
        super().parse_xml(as_dict=False)
        return_data = list()
        for owasp_scan in self.xml_root:
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

    def parse_json(self):
        super().parse_json()
        parsed_input = list()
        for site in self.parsed_input.get("site", []):
            for attr in list(site.keys()):
                site[attr.strip("@")] = site.pop(attr)
            parsed_input.append(site)
        self.parsed_input = parsed_input

    def process_parsed_input_for_template(self):
        data = dict()
        for site in self.parsed_input:
            title = f"{site.name} ({len(site.alerts)})"
            data[title] = site
        return data


loader = OWASPZap
