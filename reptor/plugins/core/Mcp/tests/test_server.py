from unittest.mock import MagicMock, patch
from reptor.plugins.core.Mcp.Server import MCPServer, MCP_SERVER_INSTRUCTIONS


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
