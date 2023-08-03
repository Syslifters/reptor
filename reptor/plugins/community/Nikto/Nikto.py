import typing
from xml.etree import ElementTree

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.plugins.community.Nikto.models import (
    NiktoScan,
    ScanDetails,
    Item,
    Statistics,
)

# Todo: Refactor to global --xml, --json


class Nikto(ToolBase):
    """
    Multiple Targets are not supported in JSON

    cat nikto-raw-output.txt | reptor simplelist -c format

    cat nikto-result.xml | python reptor simplelist --xml

    cat nikto-result.json | python reptor simplelist --json
    """

    meta = {
        "author": "Richard Schwabe",
        "name": "Nikto",
        "version": "1.1",
        "license": "MIT",
        "tags": ["web", "owasp"],
        "summary": "Formats Nikto output (XML)",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = "Nikto"

    def parse_xml(self):
        """Parses XML file from Nikto, tested with version 2.5.0

        Args:
            data (str): Raw String Input of XML

        Returns:
            typing.List[NiktoScan]: Returns a list of NiktoScan objects
        """
        self.debug("Running parse_xml of nikto")

        return_data = list()
        for niktoscan in self.xml_root:
            self.debug(f"Got niktoscan: {niktoscan} ")
            nikto = NiktoScan()
            nikto.parse(niktoscan)

            scandetails = ScanDetails()
            scandetails.parse(niktoscan[0])

            statistics = Statistics()
            statistics.parse(niktoscan[0].find("statistics"))

            for item_data in niktoscan[0].iter("item"):
                item = Item()
                item.parse(item_data)
                scandetails.append_item(item)

            nikto.statistics = statistics
            nikto.scandetails = scandetails

            return_data.append(nikto)

        self.parsed_input = return_data

    # def format(self):
    #     super().format()

    #     output = list()

    #     nikto_scans: typing.List[NiktoScan] = self.parsed_input

    #     for nikto_scan in nikto_scans:
    #         nikto_output = f"""

    #         # Nikto Scan Results

    #         CMD Options: `{nikto_scan.options}`

    #         ## Details

    #         | Target | Information |
    #         | :--- | :--- |
    #         | IP | {nikto_scan.scandetails.targetip} |
    #         | Port | {nikto_scan.scandetails.targetport} |
    #         | Hostname | {nikto_scan.scandetails.targethostname} |
    #         | Sitename | {nikto_scan.scandetails.sitename} |
    #         | Host Header | {nikto_scan.scandetails.hostheader} |
    #         | Errors | {nikto_scan.scandetails.errors} |

    #         ## Statistics
    #         | Target | Information |
    #         | :--- | :--- |
    #         | Issues Items | {nikto_scan.statistics.itemsfound} |
    #         | Duration | {nikto_scan.statistics.elapsed} Seconds |
    #         | Total Checks | {nikto_scan.statistics.checks} |

    #         ## Issues
    #         | Endpoint | Method | Description | References |
    #         | :----- | :--- | :----- | :---- |"""

    #         output.append(nikto_output)

    #         for item in nikto_scan.scandetails.items:
    #             endpoint = method = description = references = ""
    #             method = item.method
    #             references = item.references

    #             if ": " in item.description:
    #                 description_split = item.description.split(": ")
    #                 endpoint = description_split[0]
    #                 description = description_split[1]
    #             else:
    #                 endpoint = "/"
    #                 description = item.description

    #             item_output = (
    #                 f"| {endpoint} | {method} | {description} | {references} |"
    #             )
    #             output.append(item_output)

    #     self.formatted_input = "\n".join(output)


loader = Nikto
