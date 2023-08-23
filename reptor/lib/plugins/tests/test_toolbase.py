import json
import os
from pathlib import Path

import pytest
from django.template import Context

from reptor.lib.exceptions import IncompatibleDesignException
from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Finding import Finding
from reptor.models.Project import Project
from reptor.models.ProjectDesign import ProjectDesign

from ..ToolBase import ToolBase


class SQLTool(ToolBase):
    def finding_sql(self):
        return {
            "payloads": ["1=2", "1=1", "1=3"],
        }


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

        SQLTool.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.sql_tool = SQLTool(reptor=self.reptor)
        self.sql_tool.input_format = "json"
        self.sql_tool.raw_input = "{}"

    def test_no_function_methods(self):
        # There should be no finding_ methods in ToolBase
        finding_method_list = [
            func
            for func in dir(ToolBase)
            if callable(getattr(ToolBase, func)) and func.startswith("finding_")
        ]
        assert len(finding_method_list) == 0

    def test_load_local_finding_template(self):
        finding = self.example_tool.get_local_template_data("idor")
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
        finding_1 = self.example_tool.get_local_template_data("idor.toml")
        assert finding == finding_1

        # Invalid finding
        invalid_finding = self.example_tool.get_local_template_data("invalid_finding")
        assert invalid_finding is None

    @pytest.mark.parametrize(
        "affected_components_template,affected_components_rendered",
        [
            ("one\ntwo", ["one", "two"]),
            ("one\n\ntwo", ["one", "two"]),
            ("one\n  \ntwo", ["one", "two"]),
            ("one\n\t\t \ntwo", ["one", "two"]),
            (
                """
                <!--{% for a in affected_components %}-->
                  <!--{{ a }}-->
                <!--{% endfor %}-->
                """,
                ["example.com", "example.org"],
            ),
        ],
    )
    def test_pre_render_lists(
        self, affected_components_template, affected_components_rendered
    ):
        django_context = Context(
            {"affected_components": ["example.com", "example.org"]}
        )
        finding_dict = {
            "data": {
                "title": "My title",
                "affected_components": affected_components_template,
            }
        }
        rendered_dict = self.example_tool.pre_render_lists(finding_dict, django_context)
        assert (
            rendered_dict["data"]["affected_components"] == affected_components_rendered
        )

    def test_pre_render_lists_exception(self):
        finding_dict = {
            "data": {
                "not_exists": "custom field",
            }
        }
        with pytest.raises(IncompatibleDesignException):
            self.example_tool.pre_render_lists(finding_dict)

        finding_dict = {}
        with pytest.raises(ValueError):
            assert self.example_tool.pre_render_lists(finding_dict) == {}

    def test_generate_findings_with_custom_fields(self):
        # Patch API query
        self.reptor.api.projects.project = Project(
            {
                "id": "db837c68-ff58-4f63-9161-d2310d71999b",
                "project_type": "c357c387-baff-42ce-8e79-eb0597c3e0e8",
            }
        )
        project_design = """{"id":"c357c387-baff-42ce-8e79-eb0597c3e0e8","created":"2023-08-23T07:28:38.416312Z","updated":"2023-08-23T07:28:38.432044Z","source":"snapshot","scope":"project","name":"Project Design","language":"en-US","details":"","assets":"","copy_of":"7db59c50-275e-4eee-8242-5fef9fbc7abd","lock_info":null,"report_template":"<div>","report_styles":"/* Global styles */","report_fields":{"title":{"type":"string","label":"Title","origin":"core","default":"TODO report title","required":true,"spellcheck":true}},"report_sections":[],"finding_fields":{"title":{"type":"string","label":"Titel","origin":"core","default":"TODO finding title","required":true,"spellcheck":true},"evidence":{"type":"markdown","label":"Evidence","origin":"custom","default":null,"required":true},"payloads":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"Payloads","origin":"custom","required":true}},"finding_field_order":[],"finding_ordering":[]}"""
        self.reptor.api.project_designs.project_design = ProjectDesign(
            json.loads(project_design)
        )

        # Generate finding with custom fields
        findings = self.sql_tool.generate_findings()
        assert len(findings) == 1
        assert findings[0].data.title.value == "SQL issue"
        assert findings[0].data.evidence.value == "My evidence"
        assert [p.value for p in findings[0].data.payloads.value] == [
            "1=2",
            "1=1",
            "1=3",
        ]
        pass

    def test_generate_findings_with_predefined_fields(self):
        self.example_tool.generate_findings()
        assert len(self.example_tool.findings) == 3

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

        # Test empty finding without template
        no_template_empty_finding = self.example_tool.findings[2]
        assert isinstance(no_template_empty_finding, Finding)
        assert no_template_empty_finding.data.title.value == "Without Template Empty"
        assert no_template_empty_finding.data.description.value == "No description"

        # Test finding without template
        no_template_finding = self.example_tool.findings[1]
        assert isinstance(no_template_finding, Finding)
        assert no_template_finding.data.title.value == "Without Template"
        assert (
            no_template_finding.data.description.value
            == f"```{json.dumps({'payload': '2=2'}, indent=2)}```"
        )
