import pytest
from unittest.mock import MagicMock
from reptor.plugins.core.Mcp.Logic import McpLogic
from reptor.models.Finding import FindingRaw
from reptor.models.FindingTemplate import FindingTemplate

class TestMCPResources:
    @pytest.fixture
    def mock_reptor(self):
        mock = MagicMock()
        mock.get_active_project_id.return_value = "test-project-id"
        return mock

    def test_list_findings_resource_summary(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock Finding
        finding_data = {
            "id": "f1",
            "status": "in-progress",
            "data": {
                "title": "SQLi",
                "severity": "high",
                "cvss": "8.8"
            }
        }
        mock_reptor.api.projects.get_findings.return_value = [FindingRaw(finding_data)]

        findings = logic.list_findings()

        # Assert - should be a summary
        assert len(findings) == 1
        assert findings[0]["id"] == "f1"
        assert findings[0]["title"] == "SQLi"
        assert findings[0]["cvss"] == "8.8"
        assert findings[0]["status"] == "in-progress"
        assert "data" not in findings[0]
        
        mock_reptor.api.projects.init_project.assert_called_with("test-project-id")
        mock_reptor.api.projects.get_findings.assert_called_once()

    def test_list_templates_resource(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        
        mock_template = MagicMock(spec=FindingTemplate)
        mock_template.id = "t1"
        mock_template.get_main_title.return_value = "Template 1"
        mock_template.source = MagicMock(value="created")
        mock_template.tags = ["web"]
        mock_reptor.api.templates.search.return_value = [mock_template]
        
        templates = logic.list_templates()
        
        # Assert
        assert len(templates) == 1
        assert templates[0]["id"] == "t1"
        assert templates[0]["title"] == "Template 1"
        assert templates[0]["source"] == "created"
        assert templates[0]["tags"] == ["web"]
        mock_reptor.api.templates.search.assert_called_once_with()
