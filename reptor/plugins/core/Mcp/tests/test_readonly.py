from unittest.mock import patch
from reptor.plugins.core.Mcp.Server import MCPServer


WRITE_TOOLS = {
    "create_finding",
    "patch_finding",
    "delete_finding",
    "reptor_patch_project_data",
    "reptor_write_note",
    "reptor_rename_note",
}

READ_TOOLS = {
    "list_findings",
    "get_finding",
    "search_templates",
    "get_template",
    "get_finding_schema",
    "reptor_get_project_schema",
    "reptor_list_sections",
    "reptor_get_section",
    "reptor_list_notes",
    "reptor_get_note",
}


class TestReadOnlyMode:
    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_default_registers_write_tools(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP")

        registered = set(server.tool_names)
        assert WRITE_TOOLS.issubset(registered)
        assert READ_TOOLS.issubset(registered)

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_read_only_hides_write_tools(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP", read_only=True)

        registered = set(server.tool_names)
        # No write tool registered
        assert registered.isdisjoint(WRITE_TOOLS)
        # All read tools still registered
        assert READ_TOOLS.issubset(registered)

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_resources_always_registered(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP", read_only=True)

        assert "sysreptor://findings" in server.resource_names
        assert "sysreptor://templates" in server.resource_names
        assert "sysreptor://notes" in server.resource_names

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_run_streamable_http(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP")
        server.run(transport="streamable-http")
        server.mcp.run.assert_called_once_with(transport="streamable-http")
