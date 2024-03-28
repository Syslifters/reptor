import json
import os
import pathlib
from unittest.mock import MagicMock, Mock

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Finding import Finding, FindingRaw
from reptor.models.Project import Project
from reptor.models.ProjectDesign import ProjectDesign
import reptor.settings as settings

from ..ToolBase import ToolBase


class SQLTool(ToolBase):
    def finding_sql(self):
        return {}


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
        pathlib.Path(os.path.dirname(__file__)) / "../tests/data/templates"
    )

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        ExampleTool.setup_class(
            pathlib.Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.example_tool = ExampleTool()
        self.example_tool.input_format = "json"
        self.example_tool.raw_input = "{}"

        SQLTool.setup_class(
            pathlib.Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.sql_tool = SQLTool()
        self.sql_tool.input_format = "json"
        self.sql_tool.raw_input = "{}"

    def test_get_plugin_dir_paths(self):
        # Mock user plugins
        settings.PLUGIN_DIRS_USER = pathlib.Path("C:\\99\\Users\\user\\.sysreptor")
        os.path.isdir = MagicMock(return_value=True)
        paths = self.sql_tool.get_plugin_dir_paths(
            pathlib.Path("C:\\11\\installation\\reptor\\plugins\\sql_tool"),
            "findings",
            skip_user_plugins=False,
        )
        # The order of the result must be preserved!!
        #####
        assert "99" in str(paths[0])
        assert "11" in str(paths[1])
        #####
        # The order of the result must be preserved!!

    def test_generate_and_push_findings(self):
        # Patch API query
        self.reptor.api.projects._project_dict = {
            "id": "db837c68-ff58-4f63-9161-d2310d71999b",
            "project_type": "c357c387-baff-42ce-8e79-eb0597c3e0e8",
        }
        project_design = """{"id":"c357c387-baff-42ce-8e79-eb0597c3e0e8","created":"2023-08-23T07:28:38.416312Z","updated":"2023-08-23T07:28:38.432044Z","source":"snapshot","scope":"project","name":"Project Design","language":"en-US","details":"","assets":"","copy_of":"7db59c50-275e-4eee-8242-5fef9fbc7abd","report_template":"<div>","report_styles":"/* Global styles */","report_fields":{"title":{"type":"string","label":"Title","origin":"core","default":"TODO report title","required":true,"spellcheck":true}},"report_sections":[],"finding_fields":{"title":{"type":"string","label":"Titel","origin":"core","default":"TODO finding title","required":true,"spellcheck":true},"evidence":{"type":"markdown","label":"Evidence","origin":"custom","default":null,"required":true},"payloads":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"Payloads","origin":"custom","required":true}},"finding_field_order":[],"finding_ordering":[]}"""
        self.reptor.api.project_designs.project_design = ProjectDesign(
            json.loads(project_design)
        )
        self.reptor.api.templates.search = Mock(return_value=[])

        # Assert "create_finding" is called if no findings exist
        self.reptor.api.projects.get_findings = Mock(return_value=[])
        self.reptor.api.projects.create_finding = MagicMock()

        self.sql_tool.generate_and_push_findings()
        assert self.reptor.api.projects.create_finding.called

        # Assert "create_finding" is not called if finding with same title exists
        finding_raw = FindingRaw({"data": {"title": "SQL issue"}})
        self.reptor.api.projects.get_findings = Mock(return_value=[finding_raw])
        self.reptor.api.projects.create_finding = MagicMock()

        self.sql_tool.generate_and_push_findings()
        assert not self.reptor.api.projects.create_finding.called

        # Assert finding is pushed if no finding from same template exists
        finding = Finding(
            {"template": "12345"}, ProjectDesign(), raise_on_unknown_fields=True
        )
        self.reptor.api.templates.search = Mock(return_value=[finding])
        self.reptor.api.templates.get_template = Mock(return_value=[finding])
        self.reptor.api.projects.get_findings = Mock(return_value=[finding_raw])
        self.sql_tool.generate_findings = Mock(return_value=None)
        self.sql_tool.findings = [finding]
        self.reptor.api.projects.create_finding_from_template = MagicMock()
        self.reptor.api.projects.update_finding = MagicMock()

        self.sql_tool.generate_and_push_findings()
        assert self.reptor.api.projects.create_finding_from_template.called
        assert self.reptor.api.projects.update_finding.called

        # Assert finding is not pushed if finding from same template exists
        finding_raw = FindingRaw({"template": "12345"})
        finding = Finding(finding_raw, ProjectDesign(), raise_on_unknown_fields=True)
        self.reptor.api.projects.get_findings = Mock(return_value=[finding_raw])
        self.reptor.api.templates.get_template = Mock(return_value=[finding])
        self.reptor.api.templates.search = Mock(return_value=[finding])
        self.sql_tool.generate_findings = Mock(return_value=None)
        self.sql_tool.findings = [finding]
        self.reptor.api.projects.create_finding_from_template = MagicMock()
        self.reptor.api.projects.update_finding = MagicMock()

        self.sql_tool.generate_and_push_findings()
        assert not self.reptor.api.projects.create_finding_from_template.called
        assert not self.reptor.api.projects.update_finding.called

    def test_no_function_methods(self):
        # There should be no finding_ methods in ToolBase
        finding_method_list = [
            func
            for func in dir(ToolBase)
            if callable(getattr(ToolBase, func)) and func.startswith("finding_")
        ]
        assert len(finding_method_list) == 0
        assert ToolBase._get_finding_methods() == []

    def test_load_local_finding_template(self):
        finding = self.example_tool.get_local_finding_template("idor")
        assert finding["data"]["title"] == "IDOR"
        assert (
            finding["data"]["description"]
            == "Insecure Direct Object Reference (IDOR) at <!--{{ idor_url }}-->"
        )
        assert (
            finding["data"]["recommendation"]
            == "<!--{% include 'recommendation.md' %}-->"
        )
        assert len(finding["data"]["references"]) == 2
        assert finding["data"]["references"][0] == "https://reference1.example.com"
        assert finding["data"]["references"][1] == "https://reference2.example.com"
        assert finding["data"]["cvss"] == "My cvss"
        assert finding["data"]["summary"] == "My summary"
        assert finding["data"]["precondition"] == "My precondition"
        assert finding["data"]["impact"] == "My impact"
        assert finding["data"]["short_recommendation"] == "My short recommendation"
        assert finding["data"]["owasp_top10_2021"] == "A01_2021"
        assert finding["data"]["wstg_category"] == "ATHZ"
        assert finding["data"]["retest_notes"] == "My restest notes"
        assert finding["data"]["retest_status"] == "open"
        assert finding["data"]["severity"] == "high"

        # Assert loading with file ext works
        finding_1 = self.example_tool.get_local_finding_template("idor.toml")
        assert finding == finding_1

        # Invalid finding
        invalid_finding = self.example_tool.get_local_finding_template(
            "invalid_finding"
        )
        assert invalid_finding is None

    def test_generate_findings_with_custom_fields(self):
        # Patch API query
        self.reptor.api.projects.project = MagicMock(
            return_value=Project(
                {
                    "id": "db837c68-ff58-4f63-9161-d2310d71999b",
                    "project_type": "c357c387-baff-42ce-8e79-eb0597c3e0e8",
                },
                ProjectDesign(),
            )
        )
        project_design = """{"id":"c357c387-baff-42ce-8e79-eb0597c3e0e8","created":"2023-08-23T07:28:38.416312Z","updated":"2023-08-23T07:28:38.432044Z","source":"snapshot","scope":"project","name":"Project Design","language":"en-US","details":"","assets":"","copy_of":"7db59c50-275e-4eee-8242-5fef9fbc7abd","report_template":"<div>","report_styles":"/* Global styles */","report_fields":{"title":{"type":"string","label":"Title","origin":"core","default":"TODO report title","required":true,"spellcheck":true}},"report_sections":[],"finding_fields":{"title":{"type":"string","label":"Titel","origin":"core","default":"TODO finding title","required":true,"spellcheck":true},"evidence":{"type":"markdown","label":"Evidence","origin":"custom","default":null,"required":true},"payloads":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"Payloads","origin":"custom","required":true},"references":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"References","origin":"custom","required":true}},"finding_field_order":[],"finding_ordering":[]}"""
        self.reptor.api.project_designs.project_design = ProjectDesign(
            json.loads(project_design)
        )
        self.reptor.api.templates.search = Mock(return_value=[])

        # Generate finding with custom fields
        findings = self.sql_tool.generate_findings()
        assert len(findings) == 1
        assert findings[0].data.title.value == "SQL issue"
        assert findings[0].data.evidence.value == "My evidence"
        assert [p.value for p in findings[0].data.payloads.value] == [
            "1=1",
            "2=2",
        ]
        assert [p.value for p in findings[0].data.references.value] == [
            "https://example.com"
        ]

    def test_generate_findings_with_predefined_fields(self):
        # Patch API query
        self.reptor.api.templates.search = Mock(return_value=[])
        self.example_tool._project_design = ProjectDesign(
            settings.DEFAULT_PROJECT_DESIGN
        )

        self.example_tool.generate_findings()
        assert len(self.example_tool.findings) == 1

        idor_finding = self.example_tool.findings[0]
        assert isinstance(idor_finding, Finding)
        assert idor_finding.data.title.value == "IDOR"
        assert (
            idor_finding.data.description.value
            == "Insecure Direct Object Reference (IDOR) at https://example.com/idor/1337"
        )
        assert (
            idor_finding.data.recommendation.value
            == "Please fix the IDOR at https://example.com/idor/1337!"
        )
        assert idor_finding.data.cvss.value == "My cvss"
        assert idor_finding.data.summary.value == "My summary"
        assert idor_finding.data.precondition.value == "My precondition"
        assert idor_finding.data.impact.value == "My impact"
        assert idor_finding.data.short_recommendation.value == "My short recommendation"
        assert len(idor_finding.data.references.value) == 2
        assert (
            idor_finding.data.references.value[0].value
            == "https://reference1.example.com"
        )
        assert (
            idor_finding.data.references.value[1].value
            == "https://reference2.example.com"
        )
        assert idor_finding.data.owasp_top10_2021.value == "A01_2021"
        assert idor_finding.data.wstg_category.value == "ATHZ"
        assert idor_finding.data.retest_notes.value == "My restest notes"
        assert idor_finding.data.retest_status.value == "open"
        assert idor_finding.data.severity.value == "high"

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
            ("CVSS:3", "CVSS:3"),
            ("CVSS:4", "CVSS:4"),
        ],
    )
    def test_cvss2_to_3(self, cvss2, expected):
        cvss3 = self.example_tool.cvss2_to_3(cvss2)
        assert cvss3 == expected
