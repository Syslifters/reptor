from typing import Optional, List, Any, Dict

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None

from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder
from reptor.plugins.core.Mcp.Logic import McpLogic


MCP_SERVER_INSTRUCTIONS = (
    "Reptor MCP Server for SysReptor automation.\n\n"
    "⚠️ **CRITICAL: ALWAYS CHECK SCHEMA FIRST** ⚠️\n"
    "Before ANY create_finding or patch_finding call, you MUST call get_finding_schema() first.\n"
    "Field names, types, and constraints vary by project. Never assume or guess - always check.\n"
    "Skipping this step WILL result in errors. NO EXCEPTIONS.\n\n"
    "---\n\n"
    "This server allows AI agents to manage penetration testing projects and findings in SysReptor.\n\n"
    "**Project Context:**\n"
    "This server operates on the pre-configured project. The project is set via:\n"
    "- `reptor conf` command\n"
    "- Environment variable `REPTOR_PROJECT_ID`\n"
    "- CLI flag `--project-id`\n\n"
    "**Read-only mode:**\n"
    "If the server was started with `--read-only`, the write tools (create_finding, "
    "patch_finding, delete_finding, reptor_patch_project_data, reptor_write_note, "
    "reptor_rename_note) are "
    "NOT registered. Only read tools are available.\n\n"
    "**Key Workflows:**\n"
    "1. Findings: get_finding_schema → list_findings/get_finding → create_finding/patch_finding\n"
    "2. Templates: search_templates → get_template\n"
    "3. Report: reptor_get_project_schema → reptor_list_sections/reptor_get_section → reptor_patch_project_data\n"
    "4. Notes: reptor_list_notes → reptor_get_note → reptor_write_note / reptor_rename_note\n\n"
    "**Creating Findings (MANDATORY 3-Step Process)**\n"
    "1. Call get_finding_schema() to discover available fields, types, and requirements\n"
    "2. Build data dict with required fields (at minimum: title), matching schema exactly\n"
    "3. Call create_finding(data)\n\n"
    "**Updating Findings (MANDATORY Single-Field Workflow)**\n"
    "This server updates ONE field at a time:\n"
    "1. Call get_finding_schema() to understand field types and allowed values\n"
    "2. Identify the exact field name from schema (e.g., 'title', 'status', 'cvss')\n"
    "3. Construct field_value matching the schema type:\n"
    "   • string: Plain text\n"
    "   • markdown: CommonMark formatted text (use \\n for newlines, precede lists with blank line)\n"
    "   • enum: Must match one of the 'choices' from schema\n"
    "   • object: Dict matching 'properties' from schema\n"
    "   • list: Array matching 'items' definition from schema\n"
    "4. Call patch_finding(finding_id, field_name, field_value)\n"
    "5. Verify the field was updated in the returned object\n\n"
    "**Common Mistakes to Avoid:**\n"
    "- Calling create_finding/patch_finding without checking schema first\n"
    "- Assuming field names (they vary: 'description' vs 'summary', 'severity' vs 'cvss')\n"
    "- Guessing field types or enum values\n"
    "- Double-escaping markdown newlines (\\\\n instead of \\n)\n"
)


class MCPServer:
    def __init__(
        self,
        name: str = "Reptor",
        reptor_instance: Any = None,
        field_excluder: Optional[FieldExcluder] = None,
        logger: Optional[Any] = None,
        read_only: bool = False,
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        if not FastMCP:
            raise ImportError(
                "mcp library is not installed. Please install reptor[mcp]."
            )

        self.read_only = read_only
        # Names of the tools/resources actually registered (useful for tests and
        # introspection; respects read-only gating).
        self.tool_names: List[str] = []
        self.resource_names: List[str] = []

        self.mcp = FastMCP(
            name, instructions=MCP_SERVER_INSTRUCTIONS, host=host, port=port
        )

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

        @self.mcp.resource("sysreptor://notes")
        def list_notes() -> List[Dict[str, Any]]:
            """Lists all notes for the configured project."""
            return self.logic.list_notes()

        self.resource_names = ["sysreptor://findings", "sysreptor://templates", "sysreptor://notes"]

    def _register_tools(self):
        def tool(write: bool = False):
            """Register a function as an MCP tool.

            Write tools are skipped entirely when the server runs in read-only
            mode, so the model never sees a mutating tool it is not allowed to use.
            """

            def decorator(fn):
                if write and self.read_only:
                    return fn  # not registered
                self.mcp.tool()(fn)
                self.tool_names.append(fn.__name__)
                return fn

            return decorator

        # ----- Findings -----
        @tool()
        def list_findings(
            limit: Optional[int] = None, detailed: bool = False
        ) -> List[Dict[str, Any]]:
            """Lists findings for the configured project.

            By default returns a summary list (id, status, title, cvss, severity).
            Pass detailed=True to get full finding objects in one call (no extra
            requests) — handy for reading all findings at once, e.g. to learn the
            author's writing style. Use 'get_finding' for a single full finding.

            Args:
                limit: Maximum number of findings to return (default: all).
                    Must be a positive integer; non-positive values raise ValueError.
                detailed: Return full finding objects instead of summaries.
            """
            return self.logic.list_findings(limit=limit, detailed=detailed)

        @tool()
        def get_finding(finding_id: str) -> Dict[str, Any]:
            """Gets a single finding by ID.

            Returns the full finding object including vulnerability details.
            """
            return self.logic.get_finding(finding_id)

        @tool(write=True)
        def create_finding(data: Dict[str, Any]) -> Dict[str, Any]:
            """Creates a new finding in SysReptor.

            ⚠️ WARNING: You MUST call get_finding_schema() BEFORE using this tool.
            Field names and types vary by project. Guessing will cause errors.

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

        @tool(write=True)
        def patch_finding(
            finding_id: str, field_name: str, field_value: Any
        ) -> Dict[str, Any]:
            """Updates a single field on an existing finding in SysReptor.

            WARNING: You MUST call get_finding_schema() BEFORE using this tool.
            Field names, types, and allowed values vary by project. Guessing WILL fail.

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
            return an error for invalid types (the error includes the server's response body
            so you can see why it was rejected). Unknown fields are silently ignored (check the
            response to verify the field was actually updated).
            """
            return self.logic.patch_finding(finding_id, field_name, field_value)

        @tool(write=True)
        def delete_finding(finding_id: str) -> str:
            """Deletes a finding in SysReptor."""
            self.logic.delete_finding(finding_id)
            return f"Finding {finding_id} deleted."

        # ----- Templates -----
        @tool()
        def search_templates(
            query: str = "", limit: Optional[int] = None
        ) -> List[Dict[str, Any]]:
            """Searches for finding templates in SysReptor.

            Args:
                query: Search term for finding templates.
                limit: Maximum number of templates to return (default: all).
                    Must be a positive integer; non-positive values raise ValueError.

            Returns a summary list of template objects (id, title, source, tags).
            Use 'get_template' for full details.
            """
            return self.logic.search_templates(query, limit=limit)

        @tool()
        def get_template(template_id: str) -> Dict[str, Any]:
            """Gets a single finding template by ID.

            Args:
                template_id: The ID of the template.

            Returns the full template object with all translations and descriptions.
            """
            return self.logic.get_template(template_id)

        # ----- Schemas -----
        @tool()
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

        @tool()
        def reptor_get_project_schema() -> Dict[str, Any]:
            """Gets the report field schema for the configured project.

            **Call this before reptor_patch_project_data** to discover:
            - Available report field names and types
            - Required vs optional report fields
            - Enum choices for enumeration fields
            - Structure for nested object/list fields

            Returns:
                Schema with project_type and report_fields definitions including:
                - id: Field name
                - type: Field type (string, markdown, enum, list, object, etc.)
                - label: Human-readable field label
                - required: Whether the field is required
                - choices: Available values for enum fields
                - items: Item definition for list fields
                - properties: Nested field definitions for object fields
            """
            return self.logic.get_project_schema()

        # ----- Report sections -----
        @tool()
        def reptor_list_sections(limit: Optional[int] = None) -> List[Dict[str, Any]]:
            """Lists all report sections for the configured project.

            Returns a summary list of section objects (id, type, label).
            Use 'reptor_get_section' for full section data.

            Args:
                limit: Maximum number of sections to return (default: all).
                    Must be a positive integer; non-positive values raise ValueError.
            """
            return self.logic.list_sections(limit=limit)

        @tool()
        def reptor_get_section(section_id: str) -> Dict[str, Any]:
            """Gets a single report section by ID.

            Args:
                section_id: The ID of the section to retrieve.

            Returns the full section object including section data fields.
            """
            return self.logic.get_section(section_id)

        @tool(write=True)
        def reptor_patch_project_data(
            section_id: str, field_id: str, value: Any
        ) -> Dict[str, Any]:
            """Updates a single field in a report section's data.

            **WARNING: You MUST call reptor_get_project_schema() BEFORE using this tool.**
            Field names, types, and allowed values vary by project. Guessing WILL fail.

            **Mandatory workflow:**
            1. Call `reptor_get_project_schema()` to understand report field types and allowed values
            2. Identify the exact field name from the schema
            3. Construct the value matching the schema type:
               - string: Plain text
               - markdown: CommonMark formatted text (use \\n for newlines)
               - enum: Must match one of the 'choices' from schema
               - object: Dict matching 'properties' from schema
               - list: Array matching 'items' definition from schema
            4. Call this function with section_id, field_id, and value
            5. Review the returned section to verify the field was updated correctly

            Args:
                section_id: The ID of the section to update (e.g., "executive_summary").
                field_id: The ID of the field within the section's data to update.
                    Use `reptor_get_project_schema()` to discover available field names.
                value: The new value for the field. Type must match the field type in the schema
                    (string, number, boolean, object, or array depending on the field).

            Returns the updated section object with all fields.

            This tool updates one field at a time. The API validates field types and will
            return an error for invalid types (the error includes the server's response body
            so you can see why it was rejected). Unknown fields are silently ignored (check the
            response to verify the field was actually updated).
            """
            return self.logic.patch_project_data(section_id, field_id, value)

        # ----- Notes -----
        @tool()
        def reptor_list_notes(limit: Optional[int] = None) -> List[Dict[str, Any]]:
            """Lists notes for the configured project.

            Returns a navigational summary of each note (id, title, parent, order,
            checked, icon_emoji) in tree order: siblings sorted by order, children
            grouped under their parents (depth-first). Use 'reptor_get_note' to read
            the full markdown text.
            Notes hold recon data and scratch writing — useful for drafting findings
            from evidence and for learning the author's writing style.

            Args:
                limit: Maximum number of notes to return (default: all).
                    Must be a positive integer; non-positive values raise ValueError.
            """
            return self.logic.list_notes(limit=limit)

        @tool()
        def reptor_get_note(
            note_id: Optional[str] = None, title: Optional[str] = None
        ) -> Dict[str, Any]:
            """Gets a single note by ID or title, including its full markdown text.

            Args:
                note_id: The ID of the note to retrieve (preferred over title).
                title: The title of the note to retrieve (used if note_id is omitted).

            Returns the full note object including its markdown 'text'.
            """
            return self.logic.get_note(note_id=note_id, title=title)

        @tool(write=True)
        def reptor_write_note(
            title: Optional[str] = None,
            text: str = "",
            note_id: Optional[str] = None,
            parent_title: Optional[str] = None,
            timestamp: bool = False,
            overwrite: bool = False,
        ) -> Dict[str, Any]:
            """Creates a note, or appends to / replaces an existing one.

            If 'note_id' is given, 'text' is written to that note and 'title' is
            ignored. Otherwise the note is looked up (or created) by 'title'. Use
            reptor_rename_note to change a note's title.

            By default 'text' is appended, which suits running logs (recon output,
            evidence as you collect it). Set overwrite=True when 'text' is the note's
            full new content rather than an addition — e.g. a checklist whose rows
            change from [ ] to [x]. Appending such a note would grow it without bound
            and leave every historical state visible at once. When overwriting, send
            the complete note text, since anything omitted is lost.

            Args:
                title: Title of the note to write to / create (required if no note_id).
                    Ignored when note_id is set.
                text: Markdown text to write to the note.
                note_id: ID of an existing note to write to.
                parent_title: Title of a parent note to nest a newly created note under.
                timestamp: Prepend a timestamp to the inserted text.
                overwrite: Replace the note's existing text instead of appending to it.

            Returns the resulting note object.
            """
            return self.logic.write_note(
                title=title,
                text=text,
                note_id=note_id,
                parent_title=parent_title,
                timestamp=timestamp,
                overwrite=overwrite,
            )

        @tool(write=True)
        def reptor_rename_note(note_id: str, title: str) -> Dict[str, Any]:
            """Renames a note by ID.

            Args:
                note_id: ID of the note to rename.
                title: New title for the note.

            Returns the updated note object.
            """
            return self.logic.rename_note(note_id=note_id, title=title)

    def run(self, transport: str = "stdio"):
        """
        Starts the MCP server.
        """
        self.mcp.run(transport=transport)
