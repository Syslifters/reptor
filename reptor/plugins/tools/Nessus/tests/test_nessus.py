import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.ProjectDesign import ProjectDesign
from reptor.settings import DEFAULT_PROJECT_DESIGN

from ..Nessus import Nessus


class TestNessus(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Nessus.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.nessus = Nessus()

    def _load_xml_data(self, filename):
        self.nessus.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.xml")
        with open(filepath, "r") as f:
            self.nessus.raw_input = f.read()

    def test_aggregate_findings_with_severity_filter(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.severity_filter = {"medium"}
        self.nessus.parse()
        findings = self.nessus.aggregate_findings()
        assert len(findings) == 1
        assert len(findings['12218']["affected_components"]) == 2
        assert "192.168.1.112:5353 (mdns)" in findings["12218"]["affected_components"]
        assert "192.168.1.111:5353 (mdns)" in findings["12218"]["affected_components"]

    def test_parse_multi_input(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.parse()
        assert len(self.nessus.parsed_input) == 4
        self.nessus.raw_input = [self.nessus.raw_input, self.nessus.raw_input]
        self.nessus.parse()
        assert len(self.nessus.parsed_input) == 8

    def test_parse_multi_with_include(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.included_plugins = ["11219", "25216"]
        self.nessus.parse()
        p = self.nessus.parsed_input
        assert isinstance(p, list)
        assert len(p) == 2
        assert len(p[0]["findings"]) == 7
        assert len(p[1]["findings"]) == 2

    def test_parse_multi_with_exclude(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.excluded_plugins = ["11219", "25216"]
        self.nessus.parse()
        p = self.nessus.parsed_input
        assert isinstance(p, list)
        assert len(p) == 4
        assert len(p[0]["findings"]) == 5
        assert len(p[1]["findings"]) == 1

    def test_generate_findings(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.load = MagicMock(return_value=self.nessus.raw_input.encode())
        self.nessus._project_design = ProjectDesign(DEFAULT_PROJECT_DESIGN)
        self.reptor.api.templates.search = MagicMock(return_value=[])
        findings = self.nessus.generate_findings()
        assert len(findings) == 12
        assert (
            findings[0].data.title.value
            == "Samba NDR MS-RPC Request Heap-Based Remote Buffer Overflow"
        )
        assert (
            findings[11].data.title.value
            == "DNS Server hostname.bind Map Hostname Disclosure"
        )
        assert all(
            [
                f.data.cvss.value.startswith("CVSS:3.1")
                or f.data.cvss.value == ""
                or f.data.cvss.value == "n/a"
                for f in findings
            ]
        )
        assert all(
            [
                f.data.severity.value in ["info", "low", "medium", "high", "critical"]
                for f in findings
            ]
        )

        # Check correct affected componets
        assert [c.value for c in findings[0].data.affected_components.value] == [
            "10.15.10.11:443 (cifs)"
        ]
        assert [c.value for c in findings[1].data.affected_components.value] == [
            "10.15.10.11:443 (cifs)"
        ]
        assert [c.value for c in findings[2].data.affected_components.value] == [
            "10.15.10.11:53 (dns)"
        ]

        # Check plugin specific template (Service detection, plugin 22964)
        f = findings[8]
        assert f.data.title.value == "Detected network services"
        assert f.data.summary.value == "The remote service could be identified."
        assert f.data.cvss.value == "n/a"

    def test_preprocess_for_template(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.parse()
        p = self.nessus.preprocess_for_template()
        assert len(p) == 12
        assert len(set([f["plugin_name"] for f in p])) == 12
        assert all(isinstance(f.get("affected_components"), list) for f in p)
        assert p[0]["affected_components"] == ["10.15.10.11:443 (cifs)"]

        syn_finding = [f for f in p if f["pluginID"] == "11219"][0]
        affected_ips = set(
            [f.split(":")[0] for f in syn_finding["affected_components"]]
        )
        assert len(affected_ips) == 2

    def test_aggregate_findings(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.parse()
        findings = self.nessus.aggregate_findings()
        assert len(findings) == 12
        assert len(findings["11219"]["port"]) == 8
        assert len(findings["25216"]["port"]) == 1
        for finding in findings.values():
            assert (
                len(finding["port"])
                == len(finding["svc_name"])
                == len(finding["protocol"])
            )

    def test_parse_multi(self):
        self._load_xml_data("nessus_multi_host")
        self.nessus.parse()
        p = self.nessus.parsed_input
        assert isinstance(p, list)
        assert len(p) == 4
        assert p[0]["target"] == "10.15.10.11"
        assert len(p[0]["findings"]) == 12
        assert p[0]["findings"][0]["port"] == "443"
        assert p[0]["findings"][0]["svc_name"] == "cifs"
        assert isinstance(p[0]["findings"][3]["see_also"], list)
        assert len(p[0]["findings"][3]["see_also"]) == 1

    @pytest.mark.parametrize("filter", ["high-critical", "high,critical"])
    def test_parse_multi_with_severity_filter(self, filter):
        self._load_xml_data("nessus_multi_host")
        self.nessus.severity_filter = self.nessus._parse_severity_filter(filter)
        assert self.nessus.severity_filter == {"high", "critical"}
        self.nessus.parse()
        p = self.nessus.parsed_input
        assert isinstance(p, list)
        assert len(p) == 1  # Only one host with high/critical findings
        assert len(p[0]["findings"]) == 2  # Two high/critical findings

    def test_parse_single(self):
        self._load_xml_data("nessus_single_host")
        self.nessus.parse()
        p = self.nessus.parsed_input
        assert isinstance(p, list)
        assert len(p) == 1
        assert p[0]["target"] == "preprod.boardvantage.net"
        assert p[0]["host_ip"] == "12.233.108.201"
        assert len(p[0]["findings"]) == 6
        assert p[0]["findings"][0]["port"] == "0"
