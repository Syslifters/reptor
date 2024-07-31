import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.ProjectDesign import ProjectDesign
from reptor.settings import DEFAULT_PROJECT_DESIGN

from ..Burp import Burp


class TestBurp(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Burp.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.burp = Burp()

    def _load_xml_data(self, filename):
        self.burp.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.xml")
        with open(filepath, "r") as f:
            self.burp.raw_input = f.read()

    def test_generate_findings_missing_var(self):
        self._load_xml_data("burp")
        self.burp.load = MagicMock(return_value=self.burp.raw_input.encode())  # type: ignore
        self.burp._project_design = ProjectDesign(DEFAULT_PROJECT_DESIGN)
        self.reptor.api.templates.search = MagicMock(return_value=[])
        self.burp.preprocess_for_template = MagicMock(
            return_value=[
                {
                    "affected_components": [
                        "https://ginandjuice.shop/a'a%5c'b%22c%3e%3f%3e%25%7d%7d%25%25%3ec%3c[[%3f$%7b%7b%25%7d%7dcake%5c/post "
                        "(34.249.203.140)",
                    ],
                    "confidence": "Certain",
                    "finding_templates": "5243392",
                    "host": [
                        {"#text": "https://ginandjuice.shop", "@ip": "34.249.203.140"},
                    ],
                    "issueBackground": "Issue Background",
                    "issueDetailItems": {"issueDetailItem": "Other: AWSALB"},
                    "location": ["/catalog"],
                    "name": "TLS cookie without secure flag set",
                    "path": ["/catalog"],
                    "references": [],
                    "remediationBackground": "Remediation Background",
                    "serialNumber": [
                        "5305597333036717056",
                        "7187414666400253952",
                        "2235271953881709568",
                        "7889728362258169856",
                    ],
                    "severity": "info",
                    "severity_score": 0,
                    "type": "5243392",
                    "vulnerabilityClassifications": "<ul>\n"
                    "<li><a "
                    'href="https://cwe.mitre.org/data/definitions/614.html">CWE-614: '
                    "Sensitive Cookie in HTTPS Session Without "
                    "'Secure' Attribute</a></li>\n"
                    "</ul>",
                }
            ]
        )
        type = "5243392"
        self.burp.included_plugins = {type}
        findings = self.burp.generate_findings()
        preprocessed = self.burp.preprocess_for_template()

        assert len(preprocessed) == len(findings)

        for finding in findings:
            assert finding.data.severity.value in self.burp.risk_mapping

    def test_parse_included_plugins(self):
        self._load_xml_data("burp")
        type = "5243392"
        self.burp.included_plugins = {type}
        self.burp.parse()
        assert len(self.burp.parsed_input) > 0
        assert all(i.get("type") == type for i in self.burp.parsed_input)

    def test_parse_excluded_plugins(self):
        self._load_xml_data("burp")
        type = "5243392"
        self.burp.excluded_plugins = {type}
        self.burp.parse()
        assert len(self.burp.parsed_input) > 0
        assert all(i.get("type") != type for i in self.burp.parsed_input)

    @pytest.mark.parametrize(
        ["severity_filter", "raises_value_error"],
        [
            ({"low"}, False),
            ({"low", "medium"}, False),
            ({"low", "medium", "high"}, False),
            ({"low", "medium", "high", "info"}, False),
            ({"low", "medium", "high", "info", "invalid"}, True),
        ],
    )
    def test_parse_severity_filter(self, severity_filter, raises_value_error):
        self._load_xml_data("burp")
        self.burp.severity_filter = severity_filter
        if raises_value_error:
            with pytest.raises(ValueError):
                self.burp.parse()
        else:
            self.burp.parse()
            assert len(self.burp.parsed_input) > 0
            assert all(
                i.get("severity") in severity_filter for i in self.burp.parsed_input
            )

    def test_preprocess_for_template(self):
        self._load_xml_data("burp")
        self.burp.parse()
        findings = self.burp.preprocess_for_template()

        types = [i.get("type") for i in findings]
        assert len(types) == len(findings)

        for finding in findings:
            assert "requestresponse" not in finding
            assert isinstance(finding.get("host", list()), list)

    def test_generate_findings(self):
        self._load_xml_data("burp")
        self.burp.load = MagicMock(return_value=self.burp.raw_input.encode())  # type: ignore
        self.burp._project_design = ProjectDesign(DEFAULT_PROJECT_DESIGN)
        self.reptor.api.templates.search = MagicMock(return_value=[])
        findings = self.burp.generate_findings()
        preprocessed = self.burp.preprocess_for_template()

        assert len(preprocessed) == len(findings)

        for finding in findings:
            assert finding.data.severity.value in self.burp.risk_mapping

    def test_aggregate_by_ip(self):
        self._load_xml_data("burp")
        self.burp.parse()
        all_findings = self.burp.parsed_input
        assert isinstance(all_findings, list)
        assert len(all_findings) > 0
        all_types = {i.get("type") for i in all_findings}
        aggregated_findings = self.burp.aggregate_by_ip()

        all_aggregated_types = set()
        for _, findings in aggregated_findings.items():
            types = [i.get("type") for i in findings]
            assert len(types) == len(findings)
            all_aggregated_types.update(types)

        assert len(aggregated_findings) > 1
        assert all_types == all_aggregated_types
