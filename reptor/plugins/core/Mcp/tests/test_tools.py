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
