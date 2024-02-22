import io
import json
from unittest.mock import MagicMock

import pytest
import tomli_w

from reptor.lib.reptor import Reptor
from reptor.models.ProjectDesign import ProjectDesignField
from reptor.models.Section import Section

from ..PushProject import PushProject


class TestPushProject:
    valid_data = {
        "report_data": {
            "title": "NEW REPORT",
            "custom_report_field": "FIELD VALUE",
        },
        "findings": [
            {
                "data": {
                    "title": "123",
                    "custom_finding_field": "FINDING FIELD VALUE",
                }
            }
        ],
    }

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reptor = Reptor()

    def get_mocked_push_project(self, projectdata):
        pp = PushProject(
            reptor=self.reptor, projectdata=io.BytesIO(projectdata.encode())
        )

        pp.reptor.api.projects.project = MagicMock()
        pp.reptor.api.projects.project.name = "my-project"
        pp.reptor.api.projects.project.sections = [
            Section({"id": "section1", "fields": ["title"]}),
            Section({"id": "section2", "fields": ["custom_report_field"]}),
        ]
        self.reptor.api.projects._project_dict = {
            "id": "db837c68-ff58-4f63-9161-d2310d71999b",
            "project_type": "c357c387-baff-42ce-8e79-eb0597c3e0e8",
        }
        pp.reptor.api.project_designs.project_design = MagicMock()
        pp.reptor.api.project_designs.project_design.report_fields = [
            ProjectDesignField({"name": "title", "type": "string"}),
            ProjectDesignField({"name": "custom_report_field", "type": "string"}),
        ]
        pp.reptor.api.project_designs.project_design.finding_fields = [
            ProjectDesignField({"name": "title", "type": "string"}),
            ProjectDesignField({"name": "custom_finding_field", "type": "string"}),
        ]
        self.reptor.api.projects.update_section = MagicMock()
        self.reptor.api.projects.create_finding = MagicMock()
        return pp

    def test_read_valid_input(self):
        pp = PushProject(reptor=self.reptor)
        for dumps in [json.dumps, tomli_w.dumps]:
            project_data = pp._read_input(content=dumps(self.valid_data))
            assert isinstance(project_data, dict)
            assert project_data["report_data"]["title"] == "NEW REPORT"
            assert project_data["report_data"]["custom_report_field"] == "FIELD VALUE"
            assert project_data["findings"][0]["data"]["title"] == "123"
            assert (
                project_data["findings"][0]["data"]["custom_finding_field"]
                == "FINDING FIELD VALUE"
            )

    def test_upload_valid_data(self):
        for dumps in [json.dumps, tomli_w.dumps]:
            pp = self.get_mocked_push_project(dumps(self.valid_data))
            pp.run()

            assert self.reptor.api.projects.update_section.call_count == 2
            assert self.reptor.api.projects.create_finding.call_count == 1

    @pytest.mark.parametrize(
        "data",
        [
            {"report_data": {"title": 123}},
            {"report_data": {"custom_report_field": 123}},
            {"findings": [{"data": {"title": 123}}]},
            {"findings": [{"data": {"custom_finding_field": 123}}]},
        ],
    )
    def test_errors(self, data):
        pp = self.get_mocked_push_project(tomli_w.dumps(data))
        with pytest.raises(ValueError):
            pp.run()
