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


loader = Nikto
