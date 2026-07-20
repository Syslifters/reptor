from unittest.mock import MagicMock, PropertyMock

import pytest

from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.models.ProjectDesign import ProjectDesignField


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

    def test_update_with_finding_fields(self):
        fields = [
            ProjectDesignField({"id": "cvss", "type": "cvss", "label": "CVSS", "origin": "core"}),
            ProjectDesignField({"id": "title", "type": "string", "label": "Title", "origin": "core"}),
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id", "name": "Test"}
        self.api.patch.return_value = mock_response

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
        assert payload["finding_fields"][1]["id"] == "title"

    def test_update_with_report_fields(self):
        fields = [
            ProjectDesignField({"id": "title", "type": "string", "label": "Title", "origin": "core"}),
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id", "name": "Test"}
        self.api.patch.return_value = mock_response

        self.api.update_project_design(
            project_design_id="test-id",
            report_fields=fields,
        )

        self.api.patch.assert_called_once()
        payload = self.api.patch.call_args[1]["json"]
        assert "report_fields" in payload
        assert len(payload["report_fields"]) == 1
        assert payload["report_fields"][0]["id"] == "title"

    def test_update_with_both_field_types(self):
        finding_fields = [
            ProjectDesignField({"id": "cvss", "type": "cvss", "label": "CVSS", "origin": "core"}),
        ]
        report_fields = [
            ProjectDesignField({"id": "title", "type": "string", "label": "Title", "origin": "core"}),
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id", "name": "Test"}
        self.api.patch.return_value = mock_response

        self.api.update_project_design(
            project_design_id="test-id",
            finding_fields=finding_fields,
            report_fields=report_fields,
        )

        payload = self.api.patch.call_args[1]["json"]
        assert "finding_fields" in payload
        assert "report_fields" in payload
        assert len(payload["finding_fields"]) == 1
        assert len(payload["report_fields"]) == 1

    def test_update_without_fields_backward_compatible(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-id", "name": "Test"}
        self.api.patch.return_value = mock_response

        self.api.update_project_design(
            project_design_id="test-id",
            report_template="<html></html>",
        )

        payload = self.api.patch.call_args[1]["json"]
        assert "finding_fields" not in payload
        assert "report_fields" not in payload
        assert payload["report_template"] == "<html></html>"
