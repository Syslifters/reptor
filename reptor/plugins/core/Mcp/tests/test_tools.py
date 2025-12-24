import pytest
from unittest.mock import MagicMock
from reptor.plugins.core.Mcp.Logic import McpLogic
from reptor.models.Finding import FindingRaw


class TestMCPFindingCRUD:
    """Tests for Finding CRUD operations."""

    # ===== CREATE TESTS =====
    def test_create_finding_tool_deanonymized(self, mock_reptor, anonymizer):
        logic = McpLogic(reptor_instance=mock_reptor, anonymizer=anonymizer)

        # We need to populate the anonymizer map so it knows how to de-anonymize
        # Use the same project_id that get_active_project_id returns
        project_id = "test-project-id"
        anon_result = anonymizer.anonymize(project_id, {"affected_components": ["1.1.1.1"]})
        mock_component = anon_result["affected_components"][0]  # Get the actual hash

        # Tool input from LLM (using the anonymized component)
        tool_input = {"title": "SQLi", "affected_components": [mock_component]}

        # Mock the return value of create_finding
        mock_reptor.api.projects.create_finding.return_value = FindingRaw({
            "id": "f1",
            "data": {
                "title": "SQLi",
                "affected_components": ["1.1.1.1"]
            }
        })

        result = logic.create_finding(tool_input)

        expected_data = {
            "data": {
                "title": "SQLi",
                "affected_components": ["1.1.1.1"]
            }
        }
        mock_reptor.api.projects.init_project.assert_called_with(project_id)
        mock_reptor.api.projects.create_finding.assert_called_once_with(expected_data)
        
        # Verify returned result is anonymized
        assert result["data"]["affected_components"][0].startswith("REDACTED_")
        assert result["data"]["affected_components"][0] == mock_component

    # ===== READ TESTS =====
    def test_get_finding_tool_anonymized(self, mock_reptor, anonymizer):
        """Test that get_finding returns anonymized data."""
        logic = McpLogic(reptor_instance=mock_reptor, anonymizer=anonymizer)

        # Mock Finding
        finding_data = {
            "id": "f1",
            "data": {
                "title": "SQLi",
                "affected_components": ["1.1.1.1"]
            }
        }
        mock_reptor.api.projects.get_finding.return_value = FindingRaw(finding_data)

        finding = logic.get_finding("f1")

        anon_component = finding["data"]["affected_components"][0]
        assert anon_component.startswith("REDACTED_")
        assert anon_component != "1.1.1.1"
        mock_reptor.api.projects.init_project.assert_called_with("test-project-id")
        mock_reptor.api.projects.get_finding.assert_called_once_with("f1")

    # ===== UPDATE TESTS =====
    def test_update_finding_tool_nested_deanonymization(self, mock_reptor, anonymizer):
        """
        Test that update_finding correctly de-anonymizes data,
        even if the input is nested in a 'data' key (as returned by get_finding).
        """
        logic = McpLogic(reptor_instance=mock_reptor, anonymizer=anonymizer)
        project_id = "test-project-id"

        # 1. Pre-calculate the redacted value for 1.1.1.1
        # We can do this by anonymizing it first
        original_data = {"affected_components": ["1.1.1.1"]}
        anonymized_result = anonymizer.anonymize(project_id, original_data)
        redacted_ip = anonymized_result["affected_components"][0]

        # 2. Simulate input from an Agent that got this data from get_finding
        # The agent might send back the whole structure including 'data' wrapper
        input_data = {
            "data": {
                "title": "Updated Title",
                "affected_components": [redacted_ip]
            }
        }

        # Mock the return value of update_finding
        mock_reptor.api.projects.update_finding.return_value = FindingRaw({
            "id": "f1",
            "data": {"title": "Updated Title", "affected_components": ["1.1.1.1"]}
        })

        result = logic.update_finding("f1", input_data)

        # Check what was passed to the API client
        call_args = mock_reptor.api.projects.update_finding.call_args
        assert call_args is not None
        _, kwargs = call_args
        # If passed as positional args:
        if not kwargs:
             args = call_args[0]
             passed_data = args[1]
        else:
             passed_data = kwargs['data']

        components = []
        if "data" in passed_data and "affected_components" in passed_data["data"]:
            components = passed_data["data"]["affected_components"]
        elif "affected_components" in passed_data:
            components = passed_data["affected_components"]

        assert "1.1.1.1" in components, f"Expected '1.1.1.1' in components, got {components}"
        assert redacted_ip not in components, "Redacted value was sent to API!"
        
        # Verify returned result is anonymized
        assert result["data"]["affected_components"][0] == redacted_ip

    # ===== DELETE TESTS =====
    def test_delete_finding_tool(self, mock_reptor):
        """Test that delete_finding calls the correct API."""
        logic = McpLogic(reptor_instance=mock_reptor)

        logic.delete_finding("f1")

        mock_reptor.api.projects.init_project.assert_called_with("test-project-id")
        mock_reptor.api.projects.delete_finding.assert_called_once_with("f1")


class TestMCPTemplateTools:
    """Tests for Template-related tools."""

    # ===== SEARCH TESTS =====
    def test_search_templates_tool(self, mock_reptor, sample_template_data):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.search.return_value = [sample_template_data]

        results = logic.search_templates("SQLi")

        assert len(results) == 1
        assert results[0]["id"] == "t1"
        assert results[0]["title"] == "Template 1"
        assert results[0]["source"] == "created"
        mock_reptor.api.templates.search.assert_called_once_with("SQLi")

    # ===== GET TEMPLATE TESTS =====
    def test_get_template_tool(self, mock_reptor, sample_template_data):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.get_template.return_value = sample_template_data

        result = logic.get_template("t1")

        assert result["id"] == "t1"
        mock_reptor.api.templates.get_template.assert_called_once_with("t1")


class TestMCPSchemaDiscovery:
    """Tests for finding schema discovery."""

    def test_get_finding_schema_tool(self, mock_reptor, sample_project_design):
        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock project
        mock_project = MagicMock()
        mock_project.project_type = "design-123"
        mock_reptor.api.projects.project = mock_project

        mock_reptor.api.project_designs.fetch_project_design.return_value = sample_project_design

        result = logic.get_finding_schema()

        assert result["project_id"] == "test-project-id"
        assert result["project_type"] == "design-123"
        assert len(result["finding_fields"]) == 3

        # Check title field
        title_field = result["finding_fields"][0]
        assert title_field["id"] == "title"
        assert title_field["type"] == "string"
        assert title_field["label"] == "Title"
        assert title_field["required"] is True
        assert "choices" not in title_field  # string fields don't have choices

        # Check severity field (enum)
        severity_field = result["finding_fields"][1]
        assert severity_field["id"] == "severity"
        assert severity_field["type"] == "enum"
        assert severity_field["required"] is True
        assert severity_field["choices"] == ["info", "low", "medium", "high", "critical"]

        # Check description field
        desc_field = result["finding_fields"][2]
        assert desc_field["id"] == "description"
        assert desc_field["type"] == "markdown"
        assert desc_field["required"] is False

        # Verify API calls
        mock_reptor.api.projects.init_project.assert_called_once_with("test-project-id")
        mock_reptor.api.project_designs.fetch_project_design.assert_called_once_with("design-123")


class TestMCPErrorHandling:
    """Tests for error handling and edge cases."""

    # ===== CONFIGURATION ERRORS =====
    def test_missing_project_configuration_error(self):
        """Test error when no project is configured (empty string)."""

        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""  # No project configured
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError) as exc_info:
            logic.list_findings()

        assert "No project configured" in str(exc_info.value)

    def test_empty_project_id_error(self):
        """Test error handling when project_id is empty string."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.create_finding({"title": "Test"})

    def test_none_project_id_error(self):
        """Test error handling when project_id is None."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = None
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.get_finding("f1")

    # ===== API ERROR HANDLING =====
    def test_api_not_found_error(self, mock_reptor):
        """Test handling of 404 errors from API."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_finding.side_effect = HTTPError("404 Not Found")

        with pytest.raises(HTTPError):
            logic.get_finding("nonexistent-id")

    def test_api_permission_error(self, mock_reptor):
        """Test handling of 403 permission errors."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.create_finding.side_effect = HTTPError("403 Forbidden")

        with pytest.raises(HTTPError):
            logic.create_finding({"title": "Test"})

    def test_api_network_timeout(self, mock_reptor):
        """Test handling of network timeout errors."""
        from requests.exceptions import Timeout

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.side_effect = Timeout("Connection timeout")

        with pytest.raises(Timeout):
            logic.list_findings()

    def test_api_connection_error(self, mock_reptor):
        """Test handling of connection errors."""
        from requests.exceptions import ConnectionError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.search.side_effect = ConnectionError("Failed to connect")

        with pytest.raises(ConnectionError):
            logic.search_templates("test")

    # ===== INVALID DATA ERRORS =====
    def test_create_finding_missing_title(self, mock_reptor):
        """Test creating finding without required title field."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        # API would typically reject this
        mock_reptor.api.projects.create_finding.side_effect = HTTPError("400 Bad Request: title is required")

        with pytest.raises(HTTPError, match="title is required"):
            logic.create_finding({"description": "Test without title"})

    def test_update_finding_invalid_id(self, mock_reptor):
        """Test updating finding with invalid ID format."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.update_finding.side_effect = HTTPError("400 Bad Request: Invalid ID")

        with pytest.raises(HTTPError, match="Invalid ID"):
            logic.update_finding("invalid@id!", {"title": "Test"})

    def test_create_finding_invalid_severity(self, mock_reptor):
        """Test creating finding with invalid severity value."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.create_finding.side_effect = HTTPError("400 Bad Request: Invalid severity")

        with pytest.raises(HTTPError, match="Invalid severity"):
            logic.create_finding({"title": "Test", "severity": "super-ultra-critical"})

    # ===== EDGE CASES =====
    def test_get_finding_empty_data(self, mock_reptor):
        """Test getting finding with empty data field."""
        logic = McpLogic(reptor_instance=mock_reptor)
        finding_data = {"id": "f1", "data": {}}
        mock_reptor.api.projects.get_finding.return_value = FindingRaw(finding_data)

        result = logic.get_finding("f1")
        assert result["id"] == "f1"
        assert result["data"] == {}

    def test_list_findings_empty_project(self, mock_reptor):
        """Test listing findings when project has no findings."""
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []

        result = logic.list_findings()
        assert result == []

    def test_search_templates_no_results(self, mock_reptor):
        """Test searching templates with no matches."""
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.search.return_value = []

        result = logic.search_templates("nonexistent-query")
        assert result == []

    def test_get_template_not_found(self, mock_reptor):
        """Test getting non-existent template."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.get_template.side_effect = HTTPError("404 Not Found")

        with pytest.raises(HTTPError):
            logic.get_template("nonexistent-template-id")

    # ===== ANONYMIZATION EDGE CASES =====
    def test_anonymize_with_none_anonymizer(self, mock_reptor, sample_finding_raw):
        """Test that operations work correctly when anonymizer is None."""
        logic = McpLogic(reptor_instance=mock_reptor, anonymizer=None)
        mock_reptor.api.projects.get_finding.return_value = sample_finding_raw

        result = logic.get_finding("f1")
        # Should return data as-is without anonymization
        assert result["data"]["affected_components"] == ["192.168.1.5"]

    def test_deanonymize_unknown_redacted_value(self, mock_reptor, anonymizer):
        """Test de-anonymization with unknown REDACTED value."""
        logic = McpLogic(reptor_instance=mock_reptor, anonymizer=anonymizer)

        # Try to create finding with REDACTED value that wasn't previously anonymized
        # According to anonymizer logic, unknown values pass through
        mock_reptor.api.projects.create_finding.return_value = FindingRaw({
            "id": "f1",
            "data": {"title": "Test", "affected_components": ["REDACTED_unknown"]}
        })

        result = logic.create_finding({
            "title": "Test",
            "affected_components": ["REDACTED_unknown"]
        })

        # Verify the API was called (de-anonymization doesn't fail on unknown tokens)
        assert mock_reptor.api.projects.create_finding.called
        # The result is now anonymized, so REDACTED_unknown becomes another REDACTED_ value
        assert result["data"]["affected_components"][0].startswith("REDACTED_")
        assert result["data"]["affected_components"][0] != "REDACTED_unknown"
