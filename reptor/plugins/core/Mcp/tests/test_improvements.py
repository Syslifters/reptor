import pytest
from unittest.mock import MagicMock
from requests import HTTPError

from reptor.plugins.core.Mcp.Logic import McpLogic
from reptor.models.Finding import FindingRaw


def _http_error_with_body(message, body):
    """Build an HTTPError whose response carries a body (like a real 4xx)."""
    response = MagicMock()
    response.text = body
    return HTTPError(message, response=response)


def _template_mock(template_id):
    t = MagicMock()
    t.id = template_id
    t.get_main_title.return_value = f"Template {template_id}"
    t.source = MagicMock(value="created")
    t.tags = ["web"]
    return t


class TestApiErrorEnrichment:
    """The MCP layer should surface the API response body in raised errors."""

    def test_patch_finding_error_includes_response_body(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.update_finding.side_effect = _http_error_with_body(
            "400 Client Error: Bad Request",
            '{"data": {"severity": ["Invalid choice."]}}',
        )

        with pytest.raises(HTTPError) as exc_info:
            logic.patch_finding("f1", "severity", "super-critical")

        message = str(exc_info.value)
        assert "400 Client Error" in message
        assert "Invalid choice." in message

    def test_create_finding_error_includes_response_body(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.create_finding.side_effect = _http_error_with_body(
            "400 Client Error: Bad Request",
            '{"title": ["This field is required."]}',
        )

        with pytest.raises(HTTPError, match="This field is required."):
            logic.create_finding({"description": "no title"})

    def test_error_without_response_body_is_unmodified(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        # HTTPError with no response attached (response is None)
        mock_reptor.api.projects.update_finding.side_effect = HTTPError(
            "404 Not Found"
        )

        with pytest.raises(HTTPError) as exc_info:
            logic.patch_finding("f1", "title", "x")

        assert str(exc_info.value) == "404 Not Found"


class TestEnsureProjectCaching:
    """init_project should run once per logic instance, not on every call."""

    def test_init_project_called_once_across_calls(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []
        mock_reptor.api.projects.get_sections.return_value = []

        logic.list_findings()
        logic.list_sections()
        logic.list_findings()

        mock_reptor.api.projects.init_project.assert_called_once_with(
            "test-project-id"
        )


class TestListFindingsSeverity:
    def test_summary_includes_severity(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        finding = FindingRaw(
            {
                "id": "f1",
                "status": "in-progress",
                "data": {"title": "SQLi", "cvss": "8.8", "severity": "high"},
            }
        )
        mock_reptor.api.projects.get_findings.return_value = [finding]

        results = logic.list_findings()

        assert results[0]["severity"] == "high"
        assert results[0]["title"] == "SQLi"
        assert results[0]["cvss"] == "8.8"


class TestListFindingsDetailed:
    def test_detailed_returns_full_objects(self, mock_reptor, field_excluder):
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=field_excluder)
        finding = FindingRaw(
            {
                "id": "f1",
                "status": "in-progress",
                "data": {
                    "title": "SQLi",
                    "description": "Long prose here",
                    "affected_components": ["1.1.1.1"],  # excluded field
                },
            }
        )
        mock_reptor.api.projects.get_findings.return_value = [finding]

        results = logic.list_findings(detailed=True)

        assert results[0]["id"] == "f1"
        # Full data present...
        assert results[0]["data"]["description"] == "Long prose here"
        # ...with field exclusion still applied
        assert "affected_components" not in results[0]["data"]
        # get_findings is a single call - no per-finding fetch
        mock_reptor.api.projects.get_findings.assert_called_once()
        mock_reptor.api.projects.get_finding.assert_not_called()


class TestResultLimits:
    def test_list_findings_limit(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        findings = [
            FindingRaw({"id": f"f{i}", "data": {"title": f"T{i}"}}) for i in range(5)
        ]
        mock_reptor.api.projects.get_findings.return_value = findings

        results = logic.list_findings(limit=2)

        assert len(results) == 2
        assert results[0]["id"] == "f0"

    def test_search_templates_limit(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.search.return_value = [
            _template_mock("t1"),
            _template_mock("t2"),
            _template_mock("t3"),
        ]

        results = logic.search_templates("web", limit=2)

        assert len(results) == 2
        mock_reptor.api.templates.search.assert_called_once_with("web")

    def test_list_templates_limit(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.templates.search.return_value = [
            _template_mock("t1"),
            _template_mock("t2"),
        ]

        results = logic.list_templates(limit=1)

        assert len(results) == 1
        mock_reptor.api.templates.search.assert_called_once_with()

    def test_list_sections_limit(self, mock_reptor):
        from reptor.models.Section import SectionRaw

        logic = McpLogic(reptor_instance=mock_reptor)
        sections = []
        for i in range(3):
            s = MagicMock(spec=SectionRaw)
            s.id = f"s{i}"
            s.label = f"Section {i}"
            sections.append(s)
        mock_reptor.api.projects.get_sections.return_value = sections

        results = logic.list_sections(limit=2)

        assert len(results) == 2
