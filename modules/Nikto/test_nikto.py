import unittest
from xml.etree import ElementTree

from modules.Nikto.models import NiktoScan


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

        self.assertEqual("-host targets.txt -Format xml -output multiple-nikto.xml", nikto_scan.options)
        self.assertEqual("2.5.0", nikto_scan.version)

if __name__ == '__main__':
    unittest.main()