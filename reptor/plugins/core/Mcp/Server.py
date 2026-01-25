from typing import Optional, List, Any, Dict

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None

from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder
from reptor.plugins.core.Mcp.Logic import McpLogic


class MCPServer:
    def __init__(
        self,
        name: str = "Reptor",
        reptor_instance: Any = None,
        field_excluder: Optional[FieldExcluder] = None,
        logger: Optional[Any] = None,
    ):
        if not FastMCP:
            raise ImportError(
                "mcp library is not installed. Please install reptor[mcp]."
            )

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

        self.mcp = FastMCP(name, instructions=instructions)

        self.logic = McpLogic(reptor_instance, field_excluder, logger=logger)

        self._register_resources()
        self._register_tools()

    def _register_resources(self):
        @self.mcp.resource("sysreptor://findings")
        def list_findings() -> List[Dict[str, Any]]:
            """Lists all findings for the configured project."""
            return self.logic.list_findings()

        @self.mcp.resource("sysreptor://templates")
        def list_templates() -> List[Dict[str, Any]]:
            """Lists all finding templates from SysReptor library."""
            return self.logic.list_templates()

    def _register_tools(self):
        @self.mcp.tool()
        def list_findings() -> List[Dict[str, Any]]:
            """Lists all findings for the configured project.

            Returns a summary list of finding objects (id, title, severity, status, cvss).
            Use 'get_finding' for full details.
            """
            return self.logic.list_findings()

        @self.mcp.tool()
        def get_finding(finding_id: str) -> Dict[str, Any]:
            """Gets a single finding by ID.

            Returns the full finding object including vulnerability details.
            """
            return self.logic.get_finding(finding_id)

        @self.mcp.tool()
        def create_finding(data: Dict[str, Any]) -> Dict[str, Any]:
            """Creates a new finding in SysReptor.

            **Mandatory workflow:**
            1. Call `get_finding_schema()` to understand available fields
            2. Build data dict with required fields (at minimum: title)
            3. Call this function with your data

            Args:
                data: The finding data matching the project design schema.
                    Use `get_finding_schema()` to discover available fields.

            Returns the created finding object.
            """
            return self.logic.create_finding(data)

        @self.mcp.tool()
        def patch_finding(
            finding_id: str, field_name: str, field_value: Any
        ) -> Dict[str, Any]:
            """Updates a single field on an existing finding in SysReptor.

            **Mandatory workflow:**
            1. Call `get_finding_schema()` to understand field types, allowed values, and formatting requirements
            2. Call this function with the field name and value
            3. Review the returned finding to verify the field was updated correctly

            Args:
                finding_id: The ID of the finding to update.
                field_name: The name of the field to update (e.g., "title", "status", "cvss").
                    Use `get_finding_schema()` to discover available field names.
                field_value: The new value for the field. Type must match the field type in the schema
                    (string, number, boolean, object, or array depending on the field).

            Returns the updated finding object with all fields.

            This tool updates one field at a time. The API validates field types and will
            return an error for invalid types. Unknown fields are silently ignored (check the response
            to verify the field was actually updated).
            """
            return self.logic.patch_finding(finding_id, field_name, field_value)

        @self.mcp.tool()
        def delete_finding(finding_id: str) -> str:
            """Deletes a finding in SysReptor."""

            self.logic.delete_finding(finding_id)
            return f"Finding {finding_id} deleted."

        @self.mcp.tool()
        def search_templates(query: str = "") -> List[Dict[str, Any]]:
            """Searches for finding templates in SysReptor.

            Args:
                query: Search term for finding templates.

            Returns a summary list of template objects (id, title, source, tags).
            Use 'get_template' for full details.
            """
            return self.logic.search_templates(query)

        @self.mcp.tool()
        def get_template(template_id: str) -> Dict[str, Any]:
            """Gets a single finding template by ID.

            Args:
                template_id: The ID of the template.

            Returns the full template object with all translations and descriptions.
            """
            return self.logic.get_template(template_id)

        @self.mcp.tool()
        def get_finding_schema() -> Dict[str, Any]:
            """Gets the finding field schema for the configured project.

            **Call this before create_finding or patch_finding** to discover:
            - Available field names and types
            - Required vs optional fields
            - Enum choices for enumeration fields
            - Structure for nested object/list fields

            Returns:
                Schema with project_type and finding_fields definitions including:
                - id: Field name
                - type: Field type (string, markdown, enum, list, object, etc.)
                - label: Human-readable field label
                - required: Whether the field is required
                - choices: Available values for enum fields
                - items: Item definition for list fields
                - properties: Nested field definitions for object fields
            """
            return self.logic.get_finding_schema()

    def run(self, transport: str = "stdio"):
        """
        Starts the MCP server.
        """
        self.mcp.run(transport=transport)
