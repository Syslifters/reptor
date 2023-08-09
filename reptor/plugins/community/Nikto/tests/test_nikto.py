import unittest
from xml.etree import ElementTree

from ..models import NiktoScan

import os

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin

from ..Nikto import Nikto


class NiktoTests(TestCaseToolPlugin):
    templates_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../templates")
    )

    def setUp(self) -> None:
        Nikto.set_template_vars(
            os.path.dirname(self.templates_path), skip_user_plugins=True
        )
        self.nikto = Nikto(reptor=self.reptor)
        return super().setUp()


class TestXMLParseMethods(unittest.TestCase):
    def test_nikto_scan(self):
        xml_sample = """<?xml version="1.0" ?>
<!DOCTYPE niktoscans SYSTEM "/var/lib/nikto/docs/nikto.dtd">
<niktoscans>
    <niktoscan hoststest="0" options="-host targets.txt -Format xml -output multiple-nikto.xml" version="2.5.0" scanstart="Thu Jun 29 01:21:02 2023" scanend="Thu Jan  1 02:00:00 1970" scanelapsed=" seconds" nxmlversion="1.2">
    </niktoscan>
</niktoscans>"""

        root = ElementTree.fromstring(xml_sample)

        nikto_scan = NiktoScan()

        nikto_scan.parse(root[0])

        self.assertEqual(
            "-host targets.txt -Format xml -output multiple-nikto.xml",
            nikto_scan.options,
        )
        self.assertEqual("2.5.0", nikto_scan.version)


if __name__ == "__main__":
    unittest.main()
