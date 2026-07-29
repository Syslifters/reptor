from copy import deepcopy
from unittest.mock import MagicMock

import pytest

from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.models.ProjectDesign import ProjectDesignField, merge_report_fields_into_sections


class MockReptor:
    def __init__(self):
        self._config = MagicMock()
        self._config.get.return_value = False
        self._config.get_server.return_value = "https://demo.sysre.pt"
        self._config.get_token.return_value = "test-token"

    def get_config(self):
        return self._config

    def get_active_project_id(self):
        return "test-project-id"

    def get_logger(self):
        logger = MagicMock()
        for level in ["debug", "info", "warning", "error", "success", "display", "highlight"]:
            setattr(logger, level, MagicMock())
        return logger


class TestProjectDesignsAPI:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.api = ProjectDesignsAPI(reptor=MockReptor())
        self.api.base_endpoint = "https://demo.sysre.pt/api/v1/projecttypes/"
        self.api.patch = MagicMock()
        self.api.get = MagicMock()

    def _mock_patch_response(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id", "name": "Test"}
        self.api.patch.return_value = mock_response
        return mock_response

    def test_update_with_finding_fields(self):
        fields = [
            ProjectDesignField({"id": "cvss", "type": "cvss", "label": "CVSS", "origin": "core", "default": "n/a", "required": True}),
            ProjectDesignField({"id": "title", "type": "string", "label": "Title", "origin": "core", "required": True, "spellcheck": True}),
        ]
        self._mock_patch_response()

        self.api.update_project_design(
            project_design_id="test-id",
            finding_fields=fields,
        )

        self.api.patch.assert_called_once()
        call_args = self.api.patch.call_args
        assert call_args[0][0] == "https://demo.sysre.pt/api/v1/projecttypes/test-id"
        payload = call_args[1]["json"]
        assert "finding_fields" in payload
        assert len(payload["finding_fields"]) == 2
        assert payload["finding_fields"][0]["id"] == "cvss"
        assert payload["finding_fields"][0]["type"] == "cvss"
        assert payload["finding_fields"][1]["id"] == "title"
        assert payload["finding_fields"][1]["type"] == "string"
        assert "choices" not in payload["finding_fields"][0]
        assert "items" not in payload["finding_fields"][0]

    def test_update_with_report_fields(self):
        fields = [
            ProjectDesignField({"id": "title", "type": "string", "label": "Updated Title", "origin": "core", "required": True, "spellcheck": True}),
        ]
        get_response = MagicMock()
        get_response.json.return_value = {
            "id": "test-id",
            "name": "Test",
            "report_sections": [
                {"id": "other", "label": "Other", "fields": [
                    {"id": "title", "type": "string", "label": "Title", "origin": "core", "required": True, "spellcheck": True},
                ]},
            ],
        }
        self.api.get.return_value = get_response
        self._mock_patch_response()

        self.api.update_project_design(
            project_design_id="test-id",
            report_fields=fields,
        )

        self.api.get.assert_called_once()
        self.api.patch.assert_called_once()
        payload = self.api.patch.call_args[1]["json"]
        assert "report_fields" not in payload
        assert "report_sections" in payload
        assert len(payload["report_sections"]) == 1
        assert payload["report_sections"][0]["fields"][0]["label"] == "Updated Title"
        assert payload["report_sections"][0]["fields"][0]["type"] == "string"

    def test_update_with_both_field_types(self):
        finding_fields = [
            ProjectDesignField({"id": "cvss", "type": "cvss", "label": "CVSS", "origin": "core", "default": "n/a", "required": True}),
        ]
        report_fields = [
            ProjectDesignField({"id": "title", "type": "string", "label": "Title", "origin": "core", "required": True, "spellcheck": True}),
        ]
        get_response = MagicMock()
        get_response.json.return_value = {
            "id": "test-id",
            "name": "Test",
            "report_sections": [
                {"id": "other", "label": "Other", "fields": [
                    {"id": "title", "type": "string", "label": "Title", "origin": "core", "required": True, "spellcheck": True},
                ]},
            ],
        }
        self.api.get.return_value = get_response
        self._mock_patch_response()

        self.api.update_project_design(
            project_design_id="test-id",
            finding_fields=finding_fields,
            report_fields=report_fields,
        )

        payload = self.api.patch.call_args[1]["json"]
        assert "finding_fields" in payload
        assert "report_sections" in payload
        assert "report_fields" not in payload
        assert len(payload["finding_fields"]) == 1
        assert payload["finding_fields"][0]["type"] == "cvss"

    def test_update_with_report_sections_directly(self):
        report_sections = [
            {"id": "other", "label": "Other", "fields": [
                {"id": "title", "type": "string", "label": "Direct", "origin": "core", "required": True, "spellcheck": True},
            ]},
        ]
        self._mock_patch_response()

        self.api.update_project_design(
            project_design_id="test-id",
            report_sections=report_sections,
        )

        payload = self.api.patch.call_args[1]["json"]
        assert payload["report_sections"] == report_sections
        self.api.get.assert_not_called()

    def test_update_without_fields_backward_compatible(self):
        self._mock_patch_response()

        self.api.update_project_design(
            project_design_id="test-id",
            report_template="<html></html>",
        )

        payload = self.api.patch.call_args[1]["json"]
        assert "finding_fields" not in payload
        assert "report_fields" not in payload
        assert "report_sections" not in payload
        assert "report_preview_data" not in payload
        assert payload["report_template"] == "<html></html>"


class TestMergeReportFieldsIntoSections:
    def test_replaces_existing_field_by_id(self):
        sections = [
            {"id": "other", "label": "Other", "fields": [
                {"id": "title", "type": "string", "label": "Old", "origin": "core", "required": True},
            ]},
        ]
        updated = merge_report_fields_into_sections(
            sections,
            [ProjectDesignField({"id": "title", "type": "string", "label": "New", "origin": "core", "required": True})],
        )
        assert updated[0]["fields"][0]["label"] == "New"
        assert sections[0]["fields"][0]["label"] == "Old"

    def test_appends_new_fields_to_other_section(self):
        sections = [
            {"id": "other", "label": "Other", "fields": [
                {"id": "title", "type": "string", "label": "Title", "origin": "core", "required": True},
            ]},
        ]
        updated = merge_report_fields_into_sections(
            sections,
            [ProjectDesignField({"id": "custom_field", "type": "string", "label": "Custom", "origin": "custom", "required": False})],
        )
        field_ids = [field["id"] for field in updated[0]["fields"]]
        assert "custom_field" in field_ids

    def test_creates_other_section_when_missing(self):
        sections = [
            {"id": "scope", "label": "Scope", "fields": [
                {"id": "scope", "type": "markdown", "label": "Scope", "origin": "custom", "required": True},
            ]},
        ]
        updated = merge_report_fields_into_sections(
            sections,
            [ProjectDesignField({"id": "new_field", "type": "string", "label": "New", "origin": "custom", "required": False})],
        )
        other = next(section for section in updated if section["id"] == "other")
        assert any(field["id"] == "new_field" for field in other["fields"])
