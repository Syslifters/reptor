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
        self.nessus = Nessus(reptor=self.reptor)

    def _load_xml_data(self, filename):
        self.nessus.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.xml")
        with open(filepath, "r") as f:
            self.nessus.raw_input = f.read()

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

    @pytest.mark.parametrize(
        "cvss2, expected",
        [
            ("CVSS2#AV:P", "CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N"),
            (
                "CVSS2#AV:N/AC:M/Au:M/C:P/I:C/A:N/XX:X",
                "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "CVSS2#AV:N/AC:M/Au:M/C:P/I:C/A:J",
                "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "CVSS2#AV:N/AC:M/Au:X/C:P/I:C/A:J",
                "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "AV:N/AC:L/Au:N/C:N/I:N/A:N",
                "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N",
            ),
            (
                "CVSS2#AV:N/AC:M/Au:M/C:P/I:C/A:N",
                "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "AV:N/AC:M/Au:S/C:P/I:C/A:N",
                "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "AV:N/AC:L/Au:N/C:C/I:C/A:C",
                "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            ),
            (
                "CVSS2#AV:N/AC:L/Au:N/C:P/I:N/A:N",
                "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
            ),
            (
                "AV:N/AC:M/Au:M/C:P/I:C/A:N/E:F/RL:TF/RC:C",
                "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "AV:N/AC:H/Au:M/C:P/I:C/A:N/E:F/RL:TF/RC:C/CDP:MH/TD:L/CR:H/IR:M/AR:L",
                "CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:H/A:N",
            ),
            (
                "AV:N/AC:M/Au:M/C:P/I:C/A:N/E:F/RL:ND/RC:C/CDP:ND/TD:H/CR:H/IR:M/AR:ND",
                "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N",
            ),
        ],
    )
    def test_cvss2_to_3(self, cvss2, expected):
        cvss3 = self.nessus._cvss2_to_3(cvss2)
        assert cvss3 == expected

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
                f.data.severity.value in ["none", "low", "medium", "high", "critical"]
                for f in findings
            ]
        )

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

    @pytest.mark.parametrize("filter", ["high-critical", "high,critical", "high"])
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