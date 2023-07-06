import typing
from xml.etree import ElementTree

from reptor.core.modules.ToolBase import ToolBase
from reptor.community.Nikto.models import NiktoScan, ScanDetails, Item, Statistics


class Nikto(ToolBase):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: web,owasp

    Short Help:
    Formats Nikto output (Raw, XML, JSON)

    Description:

    Multiple Targets are not supported in JSON

    cat nikto-raw-output.txt | reptor simplelist -c format

    cat nikto-result.xml | python reptor simplelist --xml

    cat nikto-result.json | python reptor simplelist --json
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = "Nikto"
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

    def parse_json(self, data) -> typing.List[NiktoScan]:
        raise NotImplementedError

    def parse_xml(self, data) -> typing.List[NiktoScan]:
        """Parses XML file from Nikto, tested with version 2.5.0

        Args:
            data (str): Raw String Input of XML

        Returns:
            typing.List[NiktoScan]: Returns a list of NiktoScan objects
        """
        root = ElementTree.fromstring(data)
        return_data = list()
        for niktoscan in root:
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

        return return_data

    def parse_raw(self, data) -> typing.List[NiktoScan]:
        raise NotImplementedError

    def parse(self):
        super().parse()

        if self.arg_type_json:
            nikto_scans = self.parse_json(self.raw_input)
        elif self.arg_type_xml:
            nikto_scans = self.parse_xml(self.raw_input)
        else:
            nikto_scans = self.parse_raw(self.raw_input)

        self.parsed_input = nikto_scans

    def format(self):
        super().format()

        output = list()

        nikto_scans: typing.List[NiktoScan] = self.parsed_input

        for nikto_scan in nikto_scans:
            nikto_output = f"""

            # Nikto Scan Results

            CMD Options: `{nikto_scan.options}`

            ## Details

            | Target | Information |
            | :--- | :--- |
            | IP | {nikto_scan.scandetails.targetip} |
            | Port | {nikto_scan.scandetails.targetport} |
            | Hostname | {nikto_scan.scandetails.targethostname} |
            | Sitename | {nikto_scan.scandetails.sitename} |
            | Host Header | {nikto_scan.scandetails.hostheader} |
            | Errors | {nikto_scan.scandetails.errors} |

            ## Statistics
            | Target | Information |
            | :--- | :--- |
            | Issues Items | {nikto_scan.statistics.itemsfound} |
            | Duration | {nikto_scan.statistics.elapsed} Seconds |
            | Total Checks | {nikto_scan.statistics.checks} |


            ## Issues
            | Endpoint | Method | Description | References |
            | :----- | :--- | :----- | :---- |"""

            output.append(nikto_output)

            for item in nikto_scan.scandetails.items:
                endpoint = method = description = references = ""
                method = item.method
                references = item.references

                if ": " in item.description:
                    description_split = item.description.split(": ")
                    endpoint = description_split[0]
                    description = description_split[1]
                else:
                    endpoint = "/"
                    description = item.description

                item_output = (
                    f"| {endpoint} | {method} | {description} | {references} |"
                )
                output.append(item_output)

        self.formatted_input = "\n".join(output)


loader = Nikto
