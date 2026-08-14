from unittest.mock import MagicMock, patch
from reptor.plugins.core.Mcp.Instructions import (
    MCP_SERVER_INSTRUCTIONS,
    build_mcp_server_instructions,
)
from reptor.plugins.core.Mcp.Server import MCPServer


class TestMCPServer:
    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_server_initialization(self, mock_fast_mcp):
        mock_instance = MagicMock()
        mock_fast_mcp.return_value = mock_instance

        server = MCPServer(name="ReptorMCP")

        mock_fast_mcp.assert_called_once_with(
            "ReptorMCP",
            instructions=MCP_SERVER_INSTRUCTIONS,
            host="127.0.0.1",
            port=8000,
        )
        assert server.mcp == mock_instance

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_custom_host_and_port_forwarded_to_fastmcp(self, mock_fast_mcp):
        mock_instance = MagicMock()
        mock_fast_mcp.return_value = mock_instance

        server = MCPServer(name="ReptorMCP", host="0.0.0.0", port=9000)

        mock_fast_mcp.assert_called_once_with(
            "ReptorMCP",
            instructions=MCP_SERVER_INSTRUCTIONS,
            host="0.0.0.0",
            port=9000,
        )
        assert server.mcp == mock_instance

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_run_stdio(self, mock_fast_mcp):
        mock_instance = MagicMock()
        mock_fast_mcp.return_value = mock_instance
        server = MCPServer(name="ReptorMCP")

        server.run(transport="stdio")

        mock_instance.run.assert_called_once_with(transport="stdio")

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_read_only_server_uses_read_only_instructions(self, mock_fast_mcp):
        mock_instance = MagicMock()
        mock_fast_mcp.return_value = mock_instance

        MCPServer(name="ReptorMCP", read_only=True)

        mock_fast_mcp.assert_called_once_with(
            "ReptorMCP",
            instructions=build_mcp_server_instructions(read_only=True),
            host="127.0.0.1",
            port=8000,
        )

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_instructions_have_consistent_workflow_structure(self, mock_fast_mcp):
        instructions = MCP_SERVER_INSTRUCTIONS

        assert "**Key Workflows:**" in instructions
        assert "**Workflow Details:**" in instructions
        assert all(
            header in instructions
            for header in ("**Findings:**", "**Templates:**", "**Report:**", "**Notes:**")
        )
        assert "1. Findings:" in instructions
        assert "2. Templates:" in instructions
        assert "3. Report:" in instructions
        assert "4. Notes:" in instructions
        assert "Creating Findings" not in instructions
