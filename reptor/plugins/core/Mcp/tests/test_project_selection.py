from unittest.mock import MagicMock

import pytest

from reptor.plugins.core.Mcp.Logic import McpLogic


def _project(pid, name, readonly=False):
    p = MagicMock()
    p.id = pid
    p.name = name
    p.tags = ["web"]
    p.language = "en-US"
    p.readonly = readonly
    return p


class TestProjectSelection:
    def test_default_project_used_when_omitted(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []

        logic.list_findings()

        mock_reptor.api.projects.init_project.assert_called_once_with(
            "test-project-id"
        )

    def test_explicit_project_id_overrides_default(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []

        logic.list_findings(project_id="other-project")

        mock_reptor.api.projects.init_project.assert_called_once_with("other-project")

    def test_default_survives_switch(self, mock_reptor):
        """init_project overwrites the active id in reptor's config; omitting
        project_id afterwards must still go back to the startup default."""
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []

        def fake_init(pid):
            mock_reptor.get_active_project_id.return_value = pid

        mock_reptor.api.projects.init_project.side_effect = fake_init

        logic.list_findings(project_id="other-project")
        logic.list_findings()

        calls = [c.args[0] for c in mock_reptor.api.projects.init_project.call_args_list]
        assert calls == ["other-project", "test-project-id"]

    def test_switch_only_when_project_changes(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []
        mock_reptor.api.projects.get_sections.return_value = []

        logic.list_findings(project_id="a")
        logic.list_sections(project_id="a")
        logic.list_findings(project_id="b")

        calls = [c.args[0] for c in mock_reptor.api.projects.init_project.call_args_list]
        assert calls == ["a", "b"]

    def test_explicit_project_works_without_default(self):
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.get_findings.return_value = []

        logic.list_findings(project_id="explicit")

        mock_reptor.api.projects.init_project.assert_called_once_with("explicit")
        with pytest.raises(ValueError, match="No project configured"):
            logic.list_findings()

    def test_list_projects(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.projects.search.return_value = [
            _project("test-project-id", "Default"),
            _project("p2", "Other", readonly=True),
        ]

        result = logic.list_projects(search="x", finished=False, limit=5)

        mock_reptor.api.projects.search.assert_called_once_with("x", finished=False)
        mock_reptor.api.projects.init_project.assert_not_called()
        assert result == [
            {
                "id": "test-project-id",
                "name": "Default",
                "tags": ["web"],
                "language": "en-US",
                "finished": False,
                "is_default": True,
            },
            {
                "id": "p2",
                "name": "Other",
                "tags": ["web"],
                "language": "en-US",
                "finished": True,
                "is_default": False,
            },
        ]


class TestProjectIdToolSchema:
    PROJECT_SCOPED = {
        "list_findings",
        "get_finding",
        "create_finding",
        "patch_finding",
        "delete_finding",
        "get_finding_schema",
        "reptor_get_project_schema",
        "reptor_list_sections",
        "reptor_get_section",
        "reptor_patch_project_data",
        "reptor_list_notes",
        "reptor_get_note",
        "reptor_write_note",
    }

    def test_project_scoped_tools_accept_project_id(self, mock_reptor):
        import asyncio

        from reptor.plugins.core.Mcp.Server import MCPServer

        server = MCPServer(reptor_instance=mock_reptor)
        tools = {t.name: t for t in asyncio.run(server.mcp.list_tools())}

        assert "list_projects" in tools
        for name in self.PROJECT_SCOPED:
            assert "project_id" in tools[name].input_schema["properties"], name
            assert "list_projects" in tools[name].description, name
        for name in ("search_templates", "get_template", "list_projects"):
            assert "project_id" not in tools[name].input_schema["properties"], name

    def test_project_id_forwarded_to_logic(self, mock_reptor):
        import asyncio

        from reptor.plugins.core.Mcp.Server import MCPServer

        server = MCPServer(reptor_instance=mock_reptor)
        server.logic = MagicMock()
        asyncio.run(
            server.mcp.call_tool(
                "delete_finding", {"finding_id": "f1", "project_id": "p2"}
            )
        )
        server.logic.delete_finding.assert_called_once_with("f1", project_id="p2")
