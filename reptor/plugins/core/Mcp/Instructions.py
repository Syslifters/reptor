from dataclasses import dataclass
from typing import Optional


READ_ONLY_SUFFIX = " (write tools unavailable in read-only mode)"

FIELD_TYPE_HINTS = (
    "   • string: Plain text\n"
    "   • markdown: CommonMark formatted text (use \\n for newlines, precede lists with blank line)\n"
    "   • enum: Must match one of the 'choices' from schema\n"
    "   • object: Dict matching 'properties' from schema\n"
    "   • list: Array matching 'items' definition from schema"
)


@dataclass(frozen=True)
class Workflow:
    name: str
    read_chain: str
    write_chain: Optional[str] = None


WORKFLOWS = (
    Workflow(
        name="Findings",
        read_chain="get_finding_schema → list_findings/get_finding",
        write_chain="create_finding/patch_finding",
    ),
    Workflow(
        name="Templates",
        read_chain="search_templates → get_template",
    ),
    Workflow(
        name="Report",
        read_chain="reptor_get_project_schema → reptor_list_sections/reptor_get_section",
        write_chain="reptor_patch_project_data",
    ),
    Workflow(
        name="Notes",
        read_chain="reptor_list_notes → reptor_get_note",
        write_chain="reptor_write_note",
    ),
)


def _format_key_workflow(index: int, workflow: Workflow, read_only: bool) -> str:
    chain = workflow.read_chain
    if workflow.write_chain and not read_only:
        chain = f"{chain} → {workflow.write_chain}"
    elif workflow.write_chain and read_only:
        chain = f"{chain}{READ_ONLY_SUFFIX}"
    return f"{index}. {workflow.name}: {chain}\n"


def build_key_workflows(read_only: bool) -> str:
    lines = ["**Key Workflows:**\n"]
    for index, workflow in enumerate(WORKFLOWS, start=1):
        lines.append(_format_key_workflow(index, workflow, read_only))
    return "".join(lines) + "\n"


def _findings_details(read_only: bool) -> str:
    read = (
        "Read: get_finding_schema to learn field names and types; list_findings "
        "(optionally detailed=True to ingest all findings at once, e.g. to learn "
        "writing style) → get_finding for a single full finding.\n"
    )
    if read_only:
        return f"**Findings:**\n{read}\n"

    write = (
        "Write: Always call get_finding_schema() before create_finding or patch_finding.\n"
        "• Create: build a data dict with required fields (at minimum: title), matching "
        "the schema exactly → create_finding(data)\n"
        "• Update: this server patches ONE field at a time — identify the exact field "
        "name from the schema, construct field_value matching its type:\n"
        f"{FIELD_TYPE_HINTS}\n"
        "→ patch_finding(finding_id, field_name, field_value) and verify the returned object\n"
        "• Delete: delete_finding(finding_id)\n"
    )
    return f"**Findings:**\n{read}{write}\n"


def _templates_details() -> str:
    return (
        "**Templates:**\n"
        "Read: search_templates → get_template for full template content from the "
        "SysReptor library. Use when drafting findings from existing write-ups.\n\n"
    )


def _report_details(read_only: bool) -> str:
    read = (
        "Read: reptor_get_project_schema to learn report field names and types → "
        "reptor_list_sections → reptor_get_section for full section data.\n"
    )
    if read_only:
        return f"**Report:**\n{read}\n"

    write = (
        "Write: Always call reptor_get_project_schema() before reptor_patch_project_data.\n"
        "This server patches ONE report field at a time — identify field_id from the schema, "
        "construct value matching its type:\n"
        f"{FIELD_TYPE_HINTS}\n"
        "→ reptor_patch_project_data(section_id, field_id, value) and verify the returned section.\n"
    )
    return f"**Report:**\n{read}{write}\n"


def _notes_details(read_only: bool) -> str:
    read = (
        "Read: reptor_list_notes → reptor_get_note for full markdown text. Notes hold "
        "recon data and scratch writing — useful for drafting findings and learning "
        "the author's writing style.\n"
    )
    if read_only:
        return f"**Notes:**\n{read}\n"

    write = (
        "Write: reptor_write_note to create, update, and rename notes.\n"
        "1. reptor_list_notes / reptor_get_note to find or read the target note\n"
        "2. reptor_write_note with note_id (preferred for updates) or title\n"
        "   • note_id only: update that existing note\n"
        "   • note_id + title: update that note and rename it\n"
        "   • title only: look up an existing note by title or create it\n"
        "3. Choose append vs overwrite:\n"
        "   • Default (append): recon logs, evidence dumps, incremental scratch text\n"
        "   • overwrite=True: checklists, status boards, or any content that represents "
        "the full current state (send complete text; omitted content is lost)\n"
    )
    return f"**Notes:**\n{read}{write}\n"


def build_workflow_details(read_only: bool) -> str:
    sections = [
        "**Workflow Details:**\n\n",
        _findings_details(read_only),
        _templates_details(),
        _report_details(read_only),
        _notes_details(read_only),
    ]
    return "".join(sections)


def build_common_mistakes(read_only: bool) -> str:
    findings = [
        "Calling create_finding/patch_finding without checking get_finding_schema first",
        "Assuming finding field names (they vary: 'description' vs 'summary', 'severity' vs 'cvss')",
        "Guessing field types or enum values",
        "Double-escaping markdown newlines (\\\\n instead of \\n)",
    ]
    report = [
        "Calling reptor_patch_project_data without checking reptor_get_project_schema first",
        "Assuming report field names or types match finding fields",
    ]
    notes = [
        "Appending to a checklist or state note instead of overwrite=True "
        "(appending keeps every historical version and the note grows without bound)",
        "Passing title together with note_id when you only meant to add text "
        "(that combination also renames the note)",
    ]

    lines = ["**Common Mistakes to Avoid:**\n", "**Findings:**\n"]
    lines.extend(f"- {item}\n" for item in findings)

    if not read_only:
        lines.append("\n**Report:**\n")
        lines.extend(f"- {item}\n" for item in report)
        lines.append("\n**Notes:**\n")
        lines.extend(f"- {item}\n" for item in notes)

    return "".join(lines)


def build_mcp_server_instructions(read_only: bool = False) -> str:
    """Build MCP server instructions tailored to the registered tool set."""
    schema_banner = (
        "⚠️ **CRITICAL: ALWAYS CHECK SCHEMA FIRST** ⚠️\n"
        "Before ANY create_finding, patch_finding, or reptor_patch_project_data call, "
        "you MUST call the relevant schema first (get_finding_schema or "
        "reptor_get_project_schema).\n"
        "Field names, types, and constraints vary by project. Never assume or guess - always check.\n"
        "Skipping this step WILL result in errors. NO EXCEPTIONS.\n\n"
    )
    if read_only:
        schema_banner = ""

    read_only_notice = (
        "**Read-only mode:**\n"
        "If the server was started with `--read-only`, the write tools (create_finding, "
        "patch_finding, delete_finding, reptor_patch_project_data, reptor_write_note) "
        "are NOT registered. Only read tools are available. "
        "The Key Workflows and Workflow Details below reflect the tools actually registered"
        + (
            " (this server is running in read-only mode)."
            if read_only
            else " (this server is not running in read-only mode; write tools are registered)."
        )
        + "\n\n"
    )

    return (
        "Reptor MCP Server for SysReptor automation.\n\n"
        + schema_banner
        + "---\n\n"
        "This server allows AI agents to manage penetration testing projects and findings in SysReptor.\n\n"
        "**Project Context:**\n"
        "This server operates on the pre-configured project. The project is set via:\n"
        "- `reptor conf` command\n"
        "- Environment variable `REPTOR_PROJECT_ID`\n"
        "- CLI flag `--project-id`\n\n"
        + read_only_notice
        + build_key_workflows(read_only)
        + build_workflow_details(read_only)
        + build_common_mistakes(read_only)
    )


# Default (write-mode) instructions; tests and imports expect this name.
MCP_SERVER_INSTRUCTIONS = build_mcp_server_instructions(read_only=False)
