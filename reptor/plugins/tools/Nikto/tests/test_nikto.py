import os
from pathlib import Path
from xml.etree import ElementTree

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin

from ..models import NiktoScan
from ..Nikto import Nikto


class TestNikto(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")
    xml_sample = """<?xml version="1.0" ?>
<!DOCTYPE niktoscans SYSTEM "/var/lib/nikto/docs/nikto.dtd">
<niktoscans>
    <niktoscan hoststest="0" options="-host targets.txt -Format xml -output multiple-nikto.xml" version="2.5.0" scanstart="Thu Jun 29 01:21:02 2023" scanend="Thu Jan  1 02:00:00 1970" scanelapsed=" seconds" nxmlversion="1.2">
    </niktoscan>
</niktoscans>"""

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Nikto.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.nikto = Nikto(reptor=self.reptor)

    def _load_xml_data(self, xml_file):
        self.nikto.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{xml_file}")
        with open(filepath, "r") as f:
            self.nikto.raw_input = f.read()

    def _load_json_data(self, json_file):
        self.nikto.input_format = "json"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{json_file}")
        with open(filepath, "r") as f:
            self.nikto.raw_input = f.read()

    def test_nikto_parse_xml(self):
        self._load_xml_data("multiple-nikto.xml")
        self.nikto.parse()
        assert len(self.nikto.parsed_input) == 2
        assert self.nikto.parsed_input[0].version == "2.5.0"
        assert self.nikto.parsed_input[1].version == "2.5.0"

        assert (
            self.nikto.parsed_input[0].options
            == "-host targets.txt -Format xml -output multiple-nikto.xml"
        )
        assert (
            self.nikto.parsed_input[1].options
            == "-host targets.txt -Format xml -output multiple-nikto.xml"
        )

        assert len(self.nikto.parsed_input[0].scandetails.items) == 2
        assert self.nikto.parsed_input[0].scandetails.errors == "0"
        assert self.nikto.parsed_input[0].scandetails.targetport == "9443"
        assert self.nikto.parsed_input[1].scandetails.targetip == "127.0.0.1"
        assert self.nikto.parsed_input[0].scandetails.targethostname == "localhost"
        assert self.nikto.parsed_input[0].scandetails.targetbanner == ""
        assert self.nikto.parsed_input[0].scandetails.starttime == "2023-06-29 01:21:03"

        assert len(self.nikto.parsed_input[1].scandetails.items) == 151
        assert (
            self.nikto.parsed_input[1].scandetails.targetbanner
            == "Apache/2.4.56 (Debian)"
        )
        assert (
            self.nikto.parsed_input[1].scandetails.targethostname
            == "mutillidae.localhost"
        )
        assert self.nikto.parsed_input[1].scandetails.targetip == "127.0.0.1"
        assert self.nikto.parsed_input[1].scandetails.targetport == "80"
        assert self.nikto.parsed_input[1].scandetails.errors == "0"
        assert self.nikto.parsed_input[1].scandetails.starttime == "2023-06-29 01:21:10"

        assert (
            self.nikto.parsed_input[1].scandetails.items[0].description
            == " Cookie PHPSESSID created without the httponly flag."
        )

    def test_nikto_format(self):
        self._load_xml_data("multiple-nikto.xml")
        self.nikto.format()

        details_table = """| Target | Information |
| :--- | :--- |
| IP | 127.0.0.1 |
| Port | 9443 |
| Hostname | localhost |
| Sitename | http://localhost:9443/ |
| Host Header | localhost |
| Errors | 0 |"""
        assert details_table in self.nikto.formatted_input

        statistics_table = """| Target | Information |
| :--- | :--- |
| Issues Items | 2 |
| Duration | 7 Seconds |
| Total Checks | None |"""
        assert statistics_table in self.nikto.formatted_input

        issues_table = """| Endpoint | Method | Description | References |
| :----- | :--- | :----- | :---- |
| / | GET |  The anti-clickjacking X-Frame-Options header is not present. | https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options |
| / | GET |  The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type. | https://www.netsparker.com/web-vulnerability-scanner/vulnerabilities/missing-content-type-header/ |"""
        assert issues_table in self.nikto.formatted_input

        scan_results = """CMD Options: `-host targets.txt -Format xml -output multiple-nikto.xml`"""
        assert scan_results in self.nikto.formatted_input

        statistics_table_1 = """| Target | Information |
| :--- | :--- |
| Issues Items | 151 |
| Duration | 15 Seconds |
| Total Checks | None |"""
        assert statistics_table_1 in self.nikto.formatted_input

        issues_table_1 = """| Endpoint | Method | Description | References |
| :----- | :--- | :----- | :---- |
| / | GET |  Cookie PHPSESSID created without the httponly flag. | https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies |
| / | GET |  Cookie showhints created without the httponly flag. | https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies |
| / | GET |  Retrieved x-powered-by header | None |"""
        assert issues_table_1 in self.nikto.formatted_input

    def test_nikto_scan(self):
        root = ElementTree.fromstring(self.xml_sample)
        nikto_scan = NiktoScan()
        nikto_scan.parse(root[0])
        assert (
            "-host targets.txt -Format xml -output multiple-nikto.xml"
            == nikto_scan.options
        )
        assert "2.5.0" == nikto_scan.version
