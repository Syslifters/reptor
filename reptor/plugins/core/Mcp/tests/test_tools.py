import pytest
from unittest.mock import MagicMock
from reptor.plugins.core.Mcp.Logic import McpLogic
from reptor.models.Finding import FindingRaw


class TestMCPFindingCRUD:
    """Tests for Finding CRUD operations."""

    # ===== CREATE TESTS =====
    def test_create_finding_tool_field_exclusion(self, mock_reptor, field_excluder):
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        project_id = "test-project-id"

        # Tool input from LLM (includes excluded field)
        tool_input = {
            "title": "SQLi",
            "affected_components": ["1.1.1.1"],
            "cvss": "8.8",
        }

        # Mock the return value of create_finding
        mock_reptor.api.projects.create_finding.return_value = FindingRaw(
            {
                "id": "f1",
                "data": {
                    "title": "SQLi",
                    "cvss": "8.8",
                    "affected_components": ["1.1.1.1"],
                },
            }
        )

        result = logic.create_finding(tool_input)

        # Verify excluded fields are removed before sending to API
        expected_data = {
            "data": {
                "title": "SQLi",
                "cvss": "8.8",
                # affected_components should be excluded
            }
        }
        mock_reptor.api.projects.init_project.assert_called_with(project_id)
        mock_reptor.api.projects.create_finding.assert_called_once_with(expected_data)

        # Verify returned result has field exclusion applied
        assert "affected_components" not in result["data"]
        assert result["data"]["title"] == "SQLi"
        assert result["data"]["cvss"] == "8.8"

    # ===== READ TESTS =====
    def test_list_findings_field_exclusion(self, mock_reptor):
        """Test that list_findings returns summaries with excluded fields removed."""
        # Create a field_excluder that excludes cvss (which IS in the summary)
        from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder

        field_excluder = FieldExcluder(exclude_fields=["cvss"])

        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Create mock FindingRaw objects with title and cvss (fields that appear in summary)
        mock_finding1 = MagicMock()
        mock_finding1.id = "f1"
        mock_finding1.status = "in-progress"
        mock_finding1.data.title = "SQL Injection"
        mock_finding1.data.cvss = "8.8"

        mock_finding2 = MagicMock()
        mock_finding2.id = "f2"
        mock_finding2.status = "completed"
        mock_finding2.data.title = "XSS"
        mock_finding2.data.cvss = "7.5"

        mock_reptor.api.projects.get_findings.return_value = [
            mock_finding1,
            mock_finding2,
        ]

        results = logic.list_findings()

        # Verify both findings are returned but cvss is excluded
        assert len(results) == 2
        # Verify excluded field is removed
        assert "cvss" not in results[0], (
            "Excluded field 'cvss' should not be in summary"
        )
        assert "cvss" not in results[1], (
            "Excluded field 'cvss' should not be in summary"
        )
        # Verify other fields are still present
        assert results[0]["id"] == "f1"
        assert results[0]["title"] == "SQL Injection"
        assert results[0]["status"] == "in-progress"
        assert results[1]["id"] == "f2"
        assert results[1]["title"] == "XSS"
        assert results[1]["status"] == "completed"
        mock_reptor.api.projects.init_project.assert_called_with("test-project-id")
        mock_reptor.api.projects.get_findings.assert_called_once()

    def test_get_finding_tool_field_exclusion(self, mock_reptor, field_excluder):
        """Test that get_finding returns data with excluded fields removed."""
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Mock Finding with excluded field
        finding_data = {
            "id": "f1",
            "data": {
                "title": "SQLi",
                "affected_components": ["1.1.1.1"],
                "cvss": "8.8",
            },
        }
        mock_reptor.api.projects.get_finding.return_value = FindingRaw(finding_data)

        finding = logic.get_finding("f1")

        # Verify excluded field is removed
        assert "affected_components" not in finding["data"]
        assert finding["data"]["title"] == "SQLi"
        assert finding["data"]["cvss"] == "8.8"
        mock_reptor.api.projects.init_project.assert_called_with("test-project-id")
        mock_reptor.api.projects.get_finding.assert_called_once_with("f1")

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

        mock_reptor.api.project_designs.get_project_design.return_value = (
            sample_project_design
        )

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
        assert severity_field["choices"] == [
            "info",
            "low",
            "medium",
            "high",
            "critical",
        ]

        # Check description field
        desc_field = result["finding_fields"][2]
        assert desc_field["id"] == "description"
        assert desc_field["type"] == "markdown"
        assert desc_field["required"] is False

        # Verify API calls
        mock_reptor.api.projects.init_project.assert_called_once_with("test-project-id")
        mock_reptor.api.project_designs.get_project_design.assert_called_once_with(
            "design-123"
        )


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
        mock_reptor.api.projects.get_findings.side_effect = Timeout(
            "Connection timeout"
        )

        with pytest.raises(Timeout):
            logic.list_findings()

    def test_api_connection_error(self, mock_reptor):
        """Test handling of connection errors."""
        from requests.exceptions import ConnectionError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.search.side_effect = ConnectionError(
            "Failed to connect"
        )

        with pytest.raises(ConnectionError):
            logic.search_templates("test")

    # ===== INVALID DATA ERRORS =====
    def test_create_finding_missing_title(self, mock_reptor):
        """Test creating finding without required title field."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        # API would typically reject this
        mock_reptor.api.projects.create_finding.side_effect = HTTPError(
            "400 Bad Request: title is required"
        )

        with pytest.raises(HTTPError, match="title is required"):
            logic.create_finding({"description": "Test without title"})

    def test_create_finding_invalid_severity(self, mock_reptor):
        """Test creating finding with invalid severity value."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.create_finding.side_effect = HTTPError(
            "400 Bad Request: Invalid severity"
        )

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

    # ===== FIELD EXCLUSION EDGE CASES =====
    def test_field_exclusion_with_none_excluder(self, mock_reptor, sample_finding_raw):
        """Test that operations work correctly when field_excluder is None."""
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=None)
        mock_reptor.api.projects.get_finding.return_value = sample_finding_raw

        result = logic.get_finding("f1")
        # Should return data as-is without field exclusion
        assert result["data"]["affected_components"] == ["192.168.1.5"]

    def test_field_exclusion_excludes_on_write(self, mock_reptor, field_excluder):
        """Test that excluded fields are removed from write operations."""
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Try to create finding with excluded field
        mock_reptor.api.projects.create_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "cvss": "5.0"}}
        )

        result = logic.create_finding(
            {
                "title": "Test",
                "affected_components": ["1.1.1.1"],  # This should be excluded
                "cvss": "5.0",
            }
        )

        # Verify the API was called without excluded field
        assert mock_reptor.api.projects.create_finding.called
        call_args = mock_reptor.api.projects.create_finding.call_args[0][0]
        assert "affected_components" not in call_args["data"], (
            "Excluded field should not be sent to API"
        )
        assert call_args["data"]["title"] == "Test"
        assert call_args["data"]["cvss"] == "5.0"

        # Verify result also has field exclusion applied
        assert "affected_components" not in result["data"]
        assert result["data"]["title"] == "Test"
        assert result["data"]["cvss"] == "5.0"


class TestMCPFindingPartialUpdate:
    """Tests for single-field partial update logic."""

    # ===== TOP-LEVEL FIELD UPDATES =====
    def test_update_finding_field_status(self, mock_reptor):
        """Test updating a top-level field (status)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock API response
        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {
                "id": "f1",
                "status": "in-progress",
                "data": {"title": "SQL Injection"},
            }
        )

        result = logic.patch_finding("f1", "status", "in-progress")

        # Verify partial payload was sent to API
        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[0] == "f1"
        assert call_args[1] == {"status": "in-progress"}

        # Verify API was initialized
        mock_reptor.api.projects.init_project.assert_called_once_with("test-project-id")

        # Verify result
        assert result["status"] == "in-progress"

    def test_update_finding_field_assignee(self, mock_reptor):
        """Test updating assignee field (top-level)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "assignee": "user1", "data": {"title": "Test"}}
        )

        result = logic.patch_finding("f1", "assignee", "user1")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"assignee": "user1"}
        assert result["assignee"] == "user1"

    def test_update_finding_field_language(self, mock_reptor):
        """Test updating language field (top-level)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "language": "en-US", "data": {"title": "Test"}}
        )

        result = logic.patch_finding("f1", "language", "en-US")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"language": "en-US"}
        assert result["language"] == "en-US"

    def test_update_finding_field_template(self, mock_reptor):
        """Test updating template field (top-level)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "template": "tpl1", "data": {"title": "Test"}}
        )

        result = logic.patch_finding("f1", "template", "tpl1")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"template": "tpl1"}
        assert result["template"] == "tpl1"

    def test_update_finding_field_order(self, mock_reptor):
        """Test updating order field (top-level)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "order": 5, "data": {"title": "Test"}}
        )

        result = logic.patch_finding("f1", "order", 5)

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"order": 5}
        assert result["order"] == 5

    # ===== DATA FIELD UPDATES (NESTED) =====
    def test_update_finding_field_title(self, mock_reptor):
        """Test updating title field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "New Title", "severity": "high"}}
        )

        result = logic.patch_finding("f1", "title", "New Title")

        # Verify partial payload with data nesting
        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"title": "New Title"}}
        assert result["data"]["title"] == "New Title"

    def test_update_finding_field_cvss(self, mock_reptor):
        """Test updating cvss field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "cvss": "9.5"}}
        )

        result = logic.patch_finding("f1", "cvss", "9.5")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"cvss": "9.5"}}
        assert result["data"]["cvss"] == "9.5"

    def test_update_finding_field_severity(self, mock_reptor):
        """Test updating severity field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "severity": "critical"}}
        )

        result = logic.patch_finding("f1", "severity", "critical")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"severity": "critical"}}
        assert result["data"]["severity"] == "critical"

    def test_update_finding_field_description(self, mock_reptor):
        """Test updating description field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "description": "Detailed desc"}}
        )

        result = logic.patch_finding("f1", "description", "Detailed desc")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"description": "Detailed desc"}}
        assert result["data"]["description"] == "Detailed desc"

    def test_update_finding_field_summary(self, mock_reptor):
        """Test updating summary field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "summary": "Brief summary"}}
        )

        result = logic.patch_finding("f1", "summary", "Brief summary")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"summary": "Brief summary"}}
        assert result["data"]["summary"] == "Brief summary"

    def test_update_finding_field_affected_components(self, mock_reptor):
        """Test updating affected_components field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "affected_components": ["1.1.1.1"]}}
        )

        result = logic.patch_finding("f1", "affected_components", ["1.1.1.1"])

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"affected_components": ["1.1.1.1"]}}
        assert result["data"]["affected_components"] == ["1.1.1.1"]

    def test_update_finding_field_precondition(self, mock_reptor):
        """Test updating precondition field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {
                "id": "f1",
                "data": {"title": "Test", "precondition": "Pre-condition text"},
            }
        )

        result = logic.patch_finding("f1", "precondition", "Pre-condition text")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"precondition": "Pre-condition text"}}
        assert result["data"]["precondition"] == "Pre-condition text"

    def test_update_finding_field_impact(self, mock_reptor):
        """Test updating impact field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "impact": "High impact"}}
        )

        result = logic.patch_finding("f1", "impact", "High impact")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"impact": "High impact"}}
        assert result["data"]["impact"] == "High impact"

    def test_update_finding_field_recommendation(self, mock_reptor):
        """Test updating recommendation field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "recommendation": "Fix it"}}
        )

        result = logic.patch_finding("f1", "recommendation", "Fix it")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"recommendation": "Fix it"}}
        assert result["data"]["recommendation"] == "Fix it"

    def test_update_finding_field_short_recommendation(self, mock_reptor):
        """Test updating short_recommendation field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "short_recommendation": "Fix"}}
        )

        result = logic.patch_finding("f1", "short_recommendation", "Fix")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"short_recommendation": "Fix"}}
        assert result["data"]["short_recommendation"] == "Fix"

    def test_update_finding_field_references(self, mock_reptor):
        """Test updating references field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {
                "id": "f1",
                "data": {"title": "Test", "references": ["https://example.com"]},
            }
        )

        result = logic.patch_finding("f1", "references", ["https://example.com"])

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"references": ["https://example.com"]}}
        assert result["data"]["references"] == ["https://example.com"]

    def test_update_finding_field_owasp_top10_2021(self, mock_reptor):
        """Test updating owasp_top10_2021 field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "owasp_top10_2021": "A01"}}
        )

        result = logic.patch_finding("f1", "owasp_top10_2021", "A01")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"owasp_top10_2021": "A01"}}
        assert result["data"]["owasp_top10_2021"] == "A01"

    def test_update_finding_field_wstg_category(self, mock_reptor):
        """Test updating wstg_category field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "wstg_category": "INFO-005"}}
        )

        result = logic.patch_finding("f1", "wstg_category", "INFO-005")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"wstg_category": "INFO-005"}}
        assert result["data"]["wstg_category"] == "INFO-005"

    def test_update_finding_field_retest_notes(self, mock_reptor):
        """Test updating retest_notes field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "retest_notes": "Retest notes"}}
        )

        result = logic.patch_finding("f1", "retest_notes", "Retest notes")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"retest_notes": "Retest notes"}}
        assert result["data"]["retest_notes"] == "Retest notes"

    def test_update_finding_field_retest_status(self, mock_reptor):
        """Test updating retest_status field (nested in data)."""
        logic = McpLogic(reptor_instance=mock_reptor)

        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "retest_status": "passed"}}
        )

        result = logic.patch_finding("f1", "retest_status", "passed")

        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"retest_status": "passed"}}
        assert result["data"]["retest_status"] == "passed"

    # ===== ERROR HANDLING =====
    def test_update_finding_field_api_error_propagation(self, mock_reptor):
        """Test that API errors are propagated without modification (Decision 4)."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock API error
        mock_reptor.api.projects.update_finding.side_effect = HTTPError(
            "404 Not Found: Finding not found"
        )

        # Verify error is propagated as-is
        with pytest.raises(HTTPError, match="404 Not Found"):
            logic.patch_finding("nonexistent-id", "title", "New Title")

    def test_update_finding_field_no_project_error(self):
        """Test error when no project is configured."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.patch_finding("f1", "title", "Test")

    # ===== FIELD EXCLUSION =====
    def test_update_finding_field_with_exclusion(self, mock_reptor, field_excluder):
        """Test that excluded fields are removed from result when field_excluder is set."""
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Update title (not excluded)
        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {
                "id": "f1",
                "data": {
                    "title": "New Title",
                    "affected_components": ["1.1.1.1"],  # Excluded field
                },
            }
        )

        result = logic.patch_finding("f1", "title", "New Title")

        # Verify payload only contains the field being updated
        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"title": "New Title"}}

        # Verify result has field exclusion applied
        assert result["data"]["title"] == "New Title"
        assert "affected_components" not in result["data"]

    def test_update_finding_field_excluded_field_write(
        self, mock_reptor, field_excluder
    ):
        """Test that trying to update an excluded field still sends it to API (no validation)."""
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Mock API accepts the update (API handles exclusion)
        mock_reptor.api.projects.update_finding.return_value = FindingRaw(
            {"id": "f1", "data": {"title": "Test", "affected_components": ["1.1.1.1"]}}
        )

        # Try to update an excluded field
        result = logic.patch_finding("f1", "affected_components", ["1.1.1.1"])

        # Verify excluded field is sent to API (no client-side validation)
        call_args = mock_reptor.api.projects.update_finding.call_args[0]
        assert call_args[1] == {"data": {"affected_components": ["1.1.1.1"]}}

        # Verify result has field exclusion applied
        assert "affected_components" not in result["data"]


class TestMCPProjectDataOperations:
    """Tests for project data operations (sections and report fields)."""

    # ===== GET PROJECT SCHEMA TESTS =====
    def test_get_project_schema_success(
        self, mock_reptor, sample_project_design_with_report_fields
    ):
        """Test successful project schema retrieval with report fields."""
        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock project
        mock_project = MagicMock()
        mock_project.project_type = "design-456"
        mock_reptor.api.projects.project = mock_project

        mock_reptor.api.project_designs.get_project_design.return_value = (
            sample_project_design_with_report_fields
        )

        result = logic.get_project_schema()

        assert result["project_id"] == "test-project-id"
        assert result["project_type"] == "design-456"
        assert len(result["report_fields"]) == 3

        # Check executive_summary field (string, required)
        exec_field = result["report_fields"][0]
        assert exec_field["id"] == "executive_summary"
        assert exec_field["type"] == "string"
        assert exec_field["label"] == "Executive Summary"
        assert exec_field["required"] is True
        assert "choices" not in exec_field

        # Check scope field (markdown, optional)
        scope_field = result["report_fields"][1]
        assert scope_field["id"] == "scope"
        assert scope_field["type"] == "markdown"
        assert scope_field["label"] == "Scope"
        assert scope_field["required"] is False

        # Check test_methodology field (enum with choices)
        method_field = result["report_fields"][2]
        assert method_field["id"] == "test_methodology"
        assert method_field["type"] == "enum"
        assert method_field["required"] is True
        assert method_field["choices"] == ["blackbox", "whitebox"]

        # Verify API calls
        mock_reptor.api.projects.init_project.assert_called_once_with("test-project-id")
        mock_reptor.api.project_designs.get_project_design.assert_called_once_with(
            "design-456"
        )

    def test_get_project_schema_api_error(self, mock_reptor):
        """Test error handling when project design fetch fails."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)

        mock_project = MagicMock()
        mock_project.project_type = "design-456"
        mock_reptor.api.projects.project = mock_project

        mock_reptor.api.project_designs.get_project_design.side_effect = HTTPError(
            "404 Not Found: Project design not found"
        )

        with pytest.raises(HTTPError, match="404 Not Found"):
            logic.get_project_schema()

    def test_get_project_schema_no_project(self):
        """Test error when no project is configured."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.get_project_schema()

    # ===== LIST SECTIONS TESTS =====
    def test_list_sections_success(self, mock_reptor):
        """Test successful section listing with metadata extraction."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor)

        # Create mock sections
        section1 = MagicMock(spec=SectionRaw)
        section1.id = "executive_summary"
        section1.label = "Executive Summary"

        section2 = MagicMock(spec=SectionRaw)
        section2.id = "scope"
        section2.label = "Scope"

        section3 = MagicMock(spec=SectionRaw)
        section3.id = "findings"
        section3.label = "Findings"

        mock_reptor.api.projects.get_sections.return_value = [
            section1,
            section2,
            section3,
        ]

        results = logic.list_sections()

        assert len(results) == 3
        assert results[0] == {
            "id": "executive_summary",
            "type": "section",
            "label": "Executive Summary",
        }
        assert results[1] == {
            "id": "scope",
            "type": "section",
            "label": "Scope",
        }
        assert results[2] == {
            "id": "findings",
            "type": "section",
            "label": "Findings",
        }

        mock_reptor.api.projects.init_project.assert_called_once_with("test-project-id")
        mock_reptor.api.projects.get_sections.assert_called_once()

    def test_list_sections_empty(self, mock_reptor):
        """Test handling empty section list."""
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_sections.return_value = []

        results = logic.list_sections()

        assert results == []
        mock_reptor.api.projects.get_sections.assert_called_once()

    def test_list_sections_with_field_exclusion(self, mock_reptor, field_excluder):
        """Test that FieldExcluder is applied to section metadata."""
        from reptor.models.Section import SectionRaw

        # Create field excluder that excludes 'label' field
        from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder

        label_excluder = FieldExcluder(exclude_fields=["label"])

        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=label_excluder)

        section1 = MagicMock(spec=SectionRaw)
        section1.id = "executive_summary"
        section1.label = "Executive Summary"

        mock_reptor.api.projects.get_sections.return_value = [section1]

        results = logic.list_sections()

        assert len(results) == 1
        assert results[0]["id"] == "executive_summary"
        assert "type" in results[0]
        assert "label" not in results[0], "Excluded field 'label' should be removed"

    def test_list_sections_no_project(self):
        """Test error when no project is configured."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.list_sections()

    # ===== GET SECTION TESTS =====
    def test_get_section_success(self, mock_reptor, sample_section_raw):
        """Test successful section retrieval."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock get_sections to return list with our section
        mock_reptor.api.projects.get_sections.return_value = [sample_section_raw]

        result = logic.get_section("executive_summary")

        assert result["id"] == "executive_summary"
        assert result["label"] == "Executive Summary"
        assert "data" in result
        assert result["data"]["executive_summary"] == "This is a test summary"

        mock_reptor.api.projects.init_project.assert_called_once_with("test-project-id")
        mock_reptor.api.projects.get_sections.assert_called_once()

    def test_get_section_with_field_exclusion(self, mock_reptor, field_excluder):
        """Test that FieldExcluder filters section.data."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Create section with excluded field
        section_data = {
            "id": "executive_summary",
            "label": "Executive Summary",
            "data": {
                "executive_summary": "Test summary",
                "affected_components": ["192.168.1.1"],  # Excluded field
            },
        }
        section = SectionRaw(section_data)
        mock_reptor.api.projects.get_sections.return_value = [section]

        result = logic.get_section("executive_summary")

        assert "affected_components" not in result["data"], (
            "Excluded field should be removed from data"
        )
        assert result["data"]["executive_summary"] == "Test summary"

    def test_get_section_not_found(self, mock_reptor):
        """Test ValueError raised when section is not found."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor)

        # Create section with different ID
        section = MagicMock(spec=SectionRaw)
        section.id = "scope"
        section.label = "Scope"

        mock_reptor.api.projects.get_sections.return_value = [section]

        with pytest.raises(ValueError, match="Section with id 'nonexistent' not found"):
            logic.get_section("nonexistent")

    def test_get_section_api_error(self, mock_reptor):
        """Test API error handling in get_section."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_sections.side_effect = HTTPError(
            "500 Internal Server Error"
        )

        with pytest.raises(HTTPError):
            logic.get_section("executive_summary")

    def test_get_section_no_project(self):
        """Test error when no project is configured."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.get_section("executive_summary")

    # ===== PATCH PROJECT DATA TESTS =====
    def test_patch_project_data_success(self, mock_reptor):
        """Test successful partial update of section data."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor)

        # Mock the updated section returned by API
        updated_section_data = {
            "id": "executive_summary",
            "label": "Executive Summary",
            "data": {
                "executive_summary": "Updated summary text",
            },
        }
        updated_section = SectionRaw(updated_section_data)
        mock_reptor.api.projects.update_section.return_value = updated_section

        result = logic.patch_project_data(
            "executive_summary", "executive_summary", "Updated summary text"
        )

        # Verify partial payload was sent (not full section)
        mock_reptor.api.projects.update_section.assert_called_once_with(
            "executive_summary",
            {"data": {"executive_summary": "Updated summary text"}},
        )

        # Verify result
        assert result["id"] == "executive_summary"
        assert result["data"]["executive_summary"] == "Updated summary text"

    def test_patch_project_data_with_field_exclusion(self, mock_reptor, field_excluder):
        """Test FieldExcluder is applied to returned data."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)

        # Mock section with excluded field in response
        updated_section_data = {
            "id": "scope",
            "label": "Scope",
            "data": {
                "scope": "Test scope",
                "affected_components": ["10.0.0.1"],  # Excluded field
            },
        }
        updated_section = SectionRaw(updated_section_data)
        mock_reptor.api.projects.update_section.return_value = updated_section

        result = logic.patch_project_data("scope", "scope", "Test scope")

        # Verify partial payload was sent
        call_args = mock_reptor.api.projects.update_section.call_args[0]
        assert call_args[1] == {"data": {"scope": "Test scope"}}

        # Verify excluded field is removed from result
        assert "affected_components" not in result["data"]
        assert result["data"]["scope"] == "Test scope"

    def test_patch_project_data_api_error(self, mock_reptor):
        """Test API error handling in patch_project_data."""
        from requests.exceptions import HTTPError

        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.update_section.side_effect = HTTPError(
            "404 Not Found: Section not found"
        )

        with pytest.raises(HTTPError, match="404 Not Found"):
            logic.patch_project_data("nonexistent", "field", "value")

    def test_patch_project_data_no_project(self):
        """Test error when no project is configured."""
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.patch_project_data("section", "field", "value")

    def test_patch_project_data_complex_value(self, mock_reptor):
        """Test patch with complex value types (lists, dicts)."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor)

        # Test with list value
        updated_section = SectionRaw(
            {
                "id": "scope",
                "data": {"scope_items": ["item1", "item2"]},
            }
        )
        mock_reptor.api.projects.update_section.return_value = updated_section

        result = logic.patch_project_data("scope", "scope_items", ["item1", "item2"])

        call_args = mock_reptor.api.projects.update_section.call_args[0]
        assert call_args[1] == {"data": {"scope_items": ["item1", "item2"]}}
        assert result["data"]["scope_items"] == ["item1", "item2"]

    def test_patch_project_data_field_excluder_none(self, mock_reptor):
        """Test that patch works when field_excluder is None."""
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=None)

        section_data = {
            "id": "executive_summary",
            "data": {"executive_summary": "Test", "other_field": "value"},
        }
        updated_section = SectionRaw(section_data)
        mock_reptor.api.projects.update_section.return_value = updated_section

        result = logic.patch_project_data(
            "executive_summary", "executive_summary", "Test"
        )

        # Should return data as-is without field exclusion
        assert result["data"]["other_field"] == "value"
