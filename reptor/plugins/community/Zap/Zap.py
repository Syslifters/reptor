from reptor.lib.plugins.ToolBase import ToolBase


class Zap(ToolBase):
    """
    Parses ZAP generated reports in either XML or JSON

    Make sure you verify what type of findings you export.

    Recommended settings are to only export Medium and higher findings
    """

    meta = {
        "author": "Richard Schwabe",
        "name": "Zap",
        "version": "1.0",
        "license": "MIT",
        "tags": ["web", "zap"],
        "summary": "Parses ZAP reports (JSON, XML)",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = kwargs.get("notename", "ZAP")
        self.multi_notes = True
        self.note_icon = "🌩️"
        if self.input_format == "raw":
            self.input_format = "json"

    def _parse_alert_data(self, data):
        return {
            "pluginid": data.find("pluginid").text,
            "alertRef": data.find("alertRef").text,
            "name": data.find("name").text,
            "riskcode": data.find("riskcode").text,
            "confidence": data.find("confidence").text,
            "riskdesc": data.find("riskdesc").text,
            "confidencedesc": data.find("confidencedesc").text,
            "desc": data.find("desc").text,
            "count": data.find("count").text,
            "solution": data.find("solution").text,
            "reference": data.find("reference").text,
            "cweid": data.find("cweid").text,
            "wascid": data.find("wascid").text,
            "sourceid": data.find("sourceid").text,
            "instances": [],
        }

    def _parse_instance_data(self, data):
        result = {
            "uri": data.find("uri").text,
            "method": data.find("method").text,
            "param": data.find("param").text,
            "attack": data.find("attack").text,
            "evidence": data.find("evidence").text,
            "otherinfo": data.find("otherinfo").text,
        }
        if data.find("requestheader"):
            result["requestheader"] = (data.find("requestheader").text,)
        if data.find("requestbody"):
            result["requestbody"] = (data.find("requestbody").text,)
        if data.find("responseheader"):
            result["responseheader"] = (data.find("responseheader").text,)
        return result

    def parse_xml(self):
        super().parse_xml(as_dict=False)
        return_data = list()
        for scan in self.xml_root:
            site = scan.attrib
            site["alerts"] = []

            for alert_item in scan[0]:
                alert = self._parse_alert_data(alert_item)

                for instance_item in alert_item.findall("./instances/instance"):
                    instance = self._parse_instance_data(instance_item)
                    alert["instances"].append(instance)

                site["alerts"].append(alert)

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

    def preprocess_for_template(self):
        data = dict()
        for site in self.parsed_input:
            title = f"{site['name']} ({len(site['alerts'])})"
            data[title] = {"data": [site]}
        data = dict(
            sorted(
                data.items(), key=lambda x: len(x[1]["data"][0]["alerts"]), reverse=True
            )
        )
        return data


loader = Zap
