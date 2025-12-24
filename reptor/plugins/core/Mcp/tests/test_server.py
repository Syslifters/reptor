from unittest.mock import MagicMock, patch
from reptor.plugins.core.Mcp.Server import MCPServer

class TestMCPServer:
    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_server_initialization(self, mock_fast_mcp):
        mock_instance = MagicMock()
        mock_fast_mcp.return_value = mock_instance
        
        server = MCPServer(name="ReptorMCP")
        
        instructions = (
            "Reptor MCP Server for SysReptor automation.\n\n"
            "This server allows AI agents to manage penetration testing projects and findings in SysReptor.\n\n"
            "**Project Context:**\n"
            "This server operates on the pre-configured project. The project is set via:\n"
            "- `reptor conf` command\n"
            "- Environment variable `REPTOR_PROJECT_ID`\n"
            "- CLI flag `--project-id`\n\n"
            "Key workflows:\n"
            "1. Findings: Use 'get_finding_schema' to discover fields, 'list_findings' or 'get_finding' to review, 'create_finding' or 'update_finding' to manage.\n"
            "2. Templates: Use 'search_templates' to find templates and 'get_template' to see full details.\n\n"
            "IMPORTANT: Finding Schema Discovery\n"
            "Finding fields vary by project design. Before creating or updating findings:\n"
            "1. You MUST call `get_finding_schema()` to get the field schema\n"
            "2. Review the returned `finding_fields` for available fields, types, and requirements\n"
            "3. Construct your data matching the schema exactly\n\n"
            "Creating Findings:\n"
            "1. Call `get_finding_schema()` to understand available fields (MANDATORY)\n"
            "2. Build data dict with required fields (at minimum: title)\n"
            "3. Call `create_finding(data)`\n\n"
            "Updating Findings:\n"
            "1. Call `get_finding(finding_id)` to get current finding data\n"
            "2. Call `get_finding_schema()` to understand field types (MANDATORY)\n"
            "3. Modify the finding data as needed\n"
            "4. Call `update_finding(finding_id, complete_data)` with FULL finding data\n\n"
            "Anonymization:\n"
            "If anonymization is enabled, 'affected_components' (like IPs or domains) will be automatically masked with realistic fake data when retrieved and restored when writing back to SysReptor. Always use the provided mock values when referring to components.\n\n"
            "**Field Formats & Markdown:**\n"
            "1. All data MUST match the types and constraints in the schema (e.g., valid CVSS strings, specific enum values).\n"
            "2. For 'markdown' fields: Follow CommonMark standards. Always precede lists with a blank line and ensure newlines are not double-escaped (use \\n, not \\\\n)."
        )

        mock_fast_mcp.assert_called_once_with(
            "ReptorMCP",
            instructions=instructions,
        )
        assert server.mcp == mock_instance

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_run_stdio(self, mock_fast_mcp):
        mock_instance = MagicMock()
        mock_fast_mcp.return_value = mock_instance
        server = MCPServer(name="ReptorMCP")
        
        server.run(transport="stdio")
        
        mock_instance.run.assert_called_once_with(transport="stdio")
