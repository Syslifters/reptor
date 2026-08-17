from unittest.mock import patch

from reptor.plugins.core.Mcp.Instructions import build_mcp_server_instructions
from reptor.plugins.core.Mcp.Server import MCPServer

WRITE_TOOLS = {
    "create_finding",
    "patch_finding",
    "delete_finding",
    "reptor_patch_project_data",
    "reptor_write_note",
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

DOMAIN_HEADERS = ("**Findings:**", "**Templates:**", "**Report:**", "**Notes:**")
READ_ONLY_SUFFIX = "write tools unavailable in read-only mode"


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
        assert registered.isdisjoint(WRITE_TOOLS)
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


class TestInstructionStructure:
    def test_write_mode_has_four_domain_sections_and_write_guidance(self):
        instructions = build_mcp_server_instructions(read_only=False)

        assert "**Workflow Details:**" in instructions
        for header in DOMAIN_HEADERS:
            assert header in instructions
        assert "Read:" in instructions
        assert instructions.count("Write:") == 3  # Findings, Report, Notes
        assert "reptor_write_note" in instructions
        assert "reptor_rename_note" not in instructions
        assert "overwrite=True" in instructions
        assert "note_id + title: update that note and rename it" in instructions
        assert "reptor_get_project_schema" in instructions
        assert "this server is not running in read-only mode" in instructions
        assert "this server is running in read-only mode" not in instructions
        assert "Creating Findings" not in instructions
        assert "Updating Findings" not in instructions
        assert "Writing Notes" not in instructions

    def test_read_only_key_workflows_mark_write_paths_unavailable(self):
        instructions = build_mcp_server_instructions(read_only=True)
        key_workflows = instructions.split("**Workflow Details:**")[0]

        assert key_workflows.count(READ_ONLY_SUFFIX) == 3
        assert "→ create_finding" not in key_workflows
        assert "→ reptor_patch_project_data" not in key_workflows
        assert "→ reptor_write_note" not in key_workflows
        assert "reptor_rename_note" not in instructions
        assert "this server is running in read-only mode" in instructions
        assert "this server is not running in read-only mode" not in instructions

    def test_read_only_detail_sections_omit_write_blocks(self):
        instructions = build_mcp_server_instructions(read_only=True)

        for header in DOMAIN_HEADERS:
            assert header in instructions

        assert "Read:" in instructions
        assert "Write:" not in instructions
        assert "overwrite=True" not in instructions
        assert "ALWAYS CHECK SCHEMA FIRST" not in instructions

    def test_write_mode_common_mistakes_grouped_by_domain(self):
        instructions = build_mcp_server_instructions(read_only=False)

        assert "**Common Mistakes to Avoid:**" in instructions
        assert "**Findings:**" in instructions.split("Common Mistakes")[-1]
        assert "**Report:**" in instructions.split("Common Mistakes")[-1]
        assert "**Notes:**" in instructions.split("Common Mistakes")[-1]
        assert "that combination also renames the note" in instructions

    def test_read_only_common_mistakes_omit_write_domains(self):
        instructions = build_mcp_server_instructions(read_only=True)

        mistakes = instructions.split("Common Mistakes")[-1]
        assert "**Findings:**" in mistakes
        assert "**Report:**" not in mistakes
        assert "**Notes:**" not in mistakes
