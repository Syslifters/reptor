import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Note import NoteTemplate
from reptor.models.ProjectDesign import ProjectDesign
from reptor.settings import DEFAULT_PROJECT_DESIGN

from ..OpenVAS import OpenVAS


class TestNessus(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        OpenVAS.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.openvas = OpenVAS(reptor=self.reptor)

    def _load_xml_data(self, filename):
        self.openvas.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.xml")
        with open(filepath, "r") as f:
            self.openvas.raw_input = f.read()

    def test_parse_with_qod_filter(self):
        self._load_xml_data("openvas")
        self.openvas.min_qod = 50
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 5

    def test_parse_with_filter(self):
        self._load_xml_data("openvas")
        self.openvas.severity_filter = {"critical"}
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 11

    def test_preprocess_for_template(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        p = self.openvas.preprocess_for_template()
        assert len(p) == 36
        assert p[0]["affected_components"] == ["10.20.0.125"]
        assert p[0]["risk_factor"] == "critical"
        assert p[0]["oid"] == "1.3.6.1.4.1.25623.1.0.103674"
        assert p[0]["oid"] in p[0]["finding_templates"]
        assert p[0]["cvss_vector"] == "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        assert len(set([f["name"] for f in p])) == 36
        assert all(isinstance(f.get("affected_components"), list) for f in p)

    def test_aggregate_by_plugin(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        a = self.openvas.aggregate_by_plugin()
        assert len(a) == 36
        assert all([len(v) == 1 for v in a])

    def test_create_notes(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        note = self.openvas.create_notes()
        assert isinstance(note, NoteTemplate)
        assert note.icon_emoji == "🦖"
        assert note.title == "OpenVAS"
        assert note.children[0].title == "10.20.0.125"
        assert len(note.children[0].children) == 36

    def test_aggregate_by_target(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        a = self.openvas.aggregate_by_target()
        assert len(a) == 1
        assert len(a[0]) == 36

    def test_parse(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 36

        # Check sorting
        severity = 10
        for finding in p:
            assert finding["severity"] <= severity
            severity = finding["severity"]

        assert p[0]["target"] == "10.20.0.125"
        assert p[0]["risk_factor"] == "critical"
        assert p[0]["host"]["ip"] == "10.20.0.125"
        assert p[0]["nvt"]["oid"] == "1.3.6.1.4.1.25623.1.0.103674"
        assert p[0]["nvt"]["tags"]["cvss_base_vector"] == "AV:N/AC:L/Au:N/C:C/I:C/A:C"
        assert p[0]["nvt"]["tags"]["summary"].startswith("The Operating System (OS)")

    def atest_parse_multi_with_exclude(self):
        self._load_xml_data("nessus_multi_host")
        self.openvas.excluded_plugins = ["11219", "25216"]
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 4
        assert len(p[0]["findings"]) == 5
        assert len(p[1]["findings"]) == 1

    def atest_generate_findings(self):
        self._load_xml_data("nessus_multi_host")
        self.openvas.load = MagicMock(return_value=self.openvas.raw_input.encode())
        self.openvas._project_design = ProjectDesign(DEFAULT_PROJECT_DESIGN)
        self.reptor.api.templates.search = MagicMock(return_value=[])
        findings = self.openvas.generate_findings()
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

        # Check plugin specific template (Service detection, plugin 22964)
        f = findings[8]
        assert f.data.title.value == "Detected network services"
        assert f.data.summary.value == "The remote service could be identified."
        assert f.data.cvss.value == "n/a"

    def atest_preprocess_for_template(self):
        self._load_xml_data("nessus_multi_host")
        self.openvas.parse()
        p = self.openvas.preprocess_for_template()
        assert len(p) == 12
        assert len(set([f["plugin_name"] for f in p])) == 12
        assert all(isinstance(f.get("affected_components"), list) for f in p)
        assert p[0]["affected_components"] == ["10.15.10.11:443 (cifs)"]

    def atest_aggregate_findings(self):
        self._load_xml_data("nessus_multi_host")
        self.openvas.parse()
        findings = self.openvas.aggregate_findings()
        assert len(findings) == 12
        assert len(findings["11219"]["port"]) == 8
        assert len(findings["25216"]["port"]) == 1
        for finding in findings.values():
            assert (
                len(finding["port"])
                == len(finding["svc_name"])
                == len(finding["protocol"])
            )

    def atest_parse_multi(self):
        self._load_xml_data("nessus_multi_host")
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 4
        assert p[0]["target"] == "10.15.10.11"
        assert len(p[0]["findings"]) == 12
        assert p[0]["findings"][0]["port"] == "443"
        assert p[0]["findings"][0]["svc_name"] == "cifs"
        assert isinstance(p[0]["findings"][3]["see_also"], list)
        assert len(p[0]["findings"][3]["see_also"]) == 1

    @pytest.mark.parametrize("filter", ["high-critical", "high,critical"])
    def atest_parse_multi_with_severity_filter(self, filter):
        self._load_xml_data("nessus_multi_host")
        self.openvas.severity_filter = self.openvas._parse_severity_filter(filter)
        assert self.openvas.severity_filter == {"high", "critical"}
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 1  # Only one host with high/critical findings
        assert len(p[0]["findings"]) == 2  # Two high/critical findings

    def atest_parse_single(self):
        self._load_xml_data("nessus_single_host")
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 1
        assert p[0]["target"] == "preprod.boardvantage.net"
        assert p[0]["host_ip"] == "12.233.108.201"
        assert len(p[0]["findings"]) == 6
        assert p[0]["findings"][0]["port"] == "0"
