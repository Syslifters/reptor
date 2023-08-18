import os
import json
import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from pathlib import Path
from reptor.models.Finding import FindingRaw

from ..ToolBase import ToolBase


class ExampleTool(ToolBase):
    def finding_idor(self):
        return {
            "idor_url": "https://example.com/idor/1337",
        }

    def finding_without_template_empty(self):
        return dict()

    def finding_without_template(self):
        return {"payload": "2=2"}

    def finding_no_finding(self):
        return None


class TestToolbase(TestCaseToolPlugin):
    templates_path = os.path.normpath(
        Path(os.path.dirname(__file__)) / "../tests/data/templates"
    )

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        ExampleTool.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.example_tool = ExampleTool(reptor=self.reptor)
        self.example_tool.input_format = "json"
        self.example_tool.raw_input = "{}"

    def test_no_function_methods(self):
        # There should be no finding_ methods in ToolBase
        finding_method_list = [
            func
            for func in dir(ToolBase)
            if callable(getattr(ToolBase, func)) and func.startswith("finding_")
        ]
        assert len(finding_method_list) == 0

    def test_load_local_finding_template(self):
        finding = self.example_tool.get_finding_from_local_template("idor")
        assert finding.data.title == "IDOR"
        assert (
            finding.data.description
            == "Insecure Direct Object Reference (IDOR) at <!--{{ idor_url }}-->"
        )
        assert finding.data.recommendation == "<!--{% include 'recommendation.md' %}-->"
        finding_1 = self.example_tool.get_finding_from_local_template("idor.toml")
        assert finding == finding_1

        invalid_finding = self.example_tool.get_finding_from_local_template(
            "invalid_finding"
        )
        assert invalid_finding is None

    def test_generate_findings(self):
        self.example_tool.generate_findings()
        assert len(self.example_tool.findings) == 3

        idor_finding = self.example_tool.findings[0]
        assert isinstance(idor_finding, FindingRaw)
        assert idor_finding.data.title == "IDOR"
        assert (
            idor_finding.data.description
            == "Insecure Direct Object Reference (IDOR) at https://example.com/idor/1337"
        )
        assert (
            idor_finding.data.recommendation
            == "Please fix the IDOR at https://example.com/idor/1337!"
        )

        no_template_empty_finding = self.example_tool.findings[2]
        assert isinstance(no_template_empty_finding, FindingRaw)
        assert no_template_empty_finding.data.title == "Without Template Empty"
        assert no_template_empty_finding.data.description == "No description"

        no_template_finding = self.example_tool.findings[1]
        assert isinstance(no_template_finding, FindingRaw)
        assert no_template_finding.data.title == "Without Template"
        assert (
            no_template_finding.data.description
            == f"```{json.dumps({'payload': '2=2'}, indent=2)}```"
        )
