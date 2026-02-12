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
            "1. Findings: Use 'get_finding_schema' to discover fields, 'list_findings' or 'get_finding' to review, 'create_finding' or 'patch_finding' to manage.\n"
            "2. Templates: Use 'search_templates' to find templates and 'get_template' to see full details.\n\n"
            "**Finding Field Schema Discovery Workflow**\n"
            "Finding fields vary by project design. Before creating or updating findings:\n"
            "1. You MUST call `get_finding_schema()` to get the field schema for the current project\n"
            "2. Review the returned `finding_fields` array for available fields, types, and requirements\n"
            "3. Construct your data matching the schema exactly\n\n"
            "**Creating Findings**\n"
            "1. Call `get_finding_schema()` to understand available fields (MANDATORY)\n"
            "2. Build data dict with required fields (at minimum: title)\n"
            "3. Call `create_finding(data)`\n\n"
            "**Updating Findings (Single-Field Workflow)**\n"
            "This server uses a single-field update workflow. You must update one field at a time.\n\n"
            "Example workflow to update a finding:\n"
            "1. Call `get_finding_schema()` to understand field types, allowed values, and formatting requirements (MANDATORY)\n"
            "2. Identify the field name from the schema (e.g., 'title', 'status', 'cvss')\n"
            "3. Construct the appropriate field_value based on the schema type:\n"
            "   - string: Plain text value\n"
            "   - markdown: Formatted text (use CommonMark, single backslash for newlines)\n"
            "   - enum: Value must match one of the choices in the schema\n"
            "   - object: Dictionary matching the properties in the schema\n"
            "   - list: Array of items matching the items definition in the schema\n"
            "4. Call `patch_finding(finding_id, field_name, field_value)` for the specific field\n"
            "5. Review the returned finding object to verify the field was updated correctly\n\n"
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
