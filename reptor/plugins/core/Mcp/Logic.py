from contextlib import contextmanager
from typing import Optional, List, Any, Dict

from requests import HTTPError


# Finding fields that live at the top level of the API payload rather than
# nested inside the "data" object. Shared by create_finding and patch_finding
# to keep their classification in sync.
TOP_LEVEL_FINDING_FIELDS = ["status", "assignee", "language", "template", "order"]


class McpLogic:
    """
    Business logic for MCP operations, decoupling SysReptor API interactions
    from the MCP transport layer.

    Note:
        This class assumes a single, pre-configured project for the lifetime of the
        instance (see ``_ensure_project``). It is not safe to share one instance
        across concurrent requests that target different projects, because switching
        projects mutates global reptor state (``reptor.api`` / active project id).
        The stdio transport processes requests sequentially, so this is fine there;
        be cautious if exposing the server over a multi-client transport.
    """

    def __init__(
        self,
        reptor_instance: Any,
        field_excluder: Optional[Any] = None,
        logger: Optional[Any] = None,
    ):
        self.reptor = reptor_instance
        self.field_excluder = field_excluder
        self.logger = logger
        # Tracks the project id we have already switched the reptor context to,
        # so we only pay for init_project() once instead of on every tool call.
        self._initialized_project_id: Optional[str] = None

    def _log(self, msg: str):
        if self.logger:
            self.logger.debug(f"{msg}")

    @contextmanager
    def _wrap_api_errors(self):
        """Enrich SysReptor API errors with the response body.

        ``requests`` raises ``HTTPError`` with a generic message (e.g.
        "400 Client Error: Bad Request for url: ...") that omits the validation
        detail the server returned in the response body. Without that body an LLM
        cannot tell *why* a write was rejected and cannot self-correct. This wraps
        the original error so the body (e.g. "severity: invalid choice") is visible,
        while leaving errors without a response body untouched.
        """
        try:
            yield
        except HTTPError as e:
            response = getattr(e, "response", None)
            body = ""
            if response is not None:
                try:
                    body = (response.text or "").strip()
                except Exception:
                    body = ""
            if body:
                raise HTTPError(f"{e}\nAPI response: {body}", response=response) from e
            raise

    def _get_project_id(self) -> str:
        """Get the configured project ID"""
        project_id = self.reptor.get_active_project_id()
        if not project_id:
            raise ValueError(
                "No project configured. Set project_id via 'reptor conf', "
                "environment variable REPTOR_PROJECT_ID, or --project-id flag."
            )
        return project_id

    def _ensure_project(self) -> str:
        """Ensure the reptor context points at the configured project.

        ``init_project`` resets the cached API manager and re-reads the project
        design, so it is comparatively expensive. We only call it the first time a
        given project id is seen for this logic instance.
        """
        project_id = self._get_project_id()
        if self._initialized_project_id != project_id:
            self.reptor.api.projects.init_project(project_id)
            self._initialized_project_id = project_id
        return project_id

    def _apply_limit(self, results: List[Any], limit: Optional[int]) -> List[Any]:
        if limit is None:
            return results
        if limit <= 0:
            raise ValueError("limit must be a positive integer (or omit for no limit)")
        return results[:limit]

    @staticmethod
    def _order_notes_tree(notes: List[Any]) -> List[Any]:
        """Return notes in depth-first tree order (siblings sorted by order)."""
        by_parent: Dict[str, List[Any]] = {}
        for note in notes:
            parent = getattr(note, "parent", None) or ""
            by_parent.setdefault(parent, []).append(note)
        for siblings in by_parent.values():
            siblings.sort(key=lambda n: (getattr(n, "order", 0) or 0, n.id))

        ordered: List[Any] = []

        def walk(parent_id: str) -> None:
            for note in by_parent.get(parent_id, []):
                ordered.append(note)
                walk(note.id)

        walk("")
        seen = {note.id for note in ordered}
        orphans = [note for note in notes if note.id not in seen]
        orphans.sort(key=lambda n: (getattr(n, "order", 0) or 0, n.id))
        ordered.extend(orphans)
        return ordered

    def list_findings(
        self, limit: Optional[int] = None, detailed: bool = False
    ) -> List[Dict[str, Any]]:
        """Lists findings for the configured project.

        By default returns a compact summary per finding. The list endpoint already
        returns full finding data in a single request, so ``detailed=True`` returns
        the complete finding objects without any extra API calls — useful for
        ingesting existing findings in one shot (e.g. to learn the author's style).

        Args:
            limit: Maximum number of findings to return. ``None`` returns all.
                Must be a positive integer; non-positive values raise ``ValueError``.
            detailed: Return full finding objects instead of summaries.
        """
        self._log(f"list_findings called (detailed={detailed})")
        self._ensure_project()
        with self._wrap_api_errors():
            findings_raw = self.reptor.api.projects.get_findings()

        results = []
        for f in findings_raw:
            if detailed:
                finding_dict = f.to_dict()
                if self.field_excluder:
                    finding_dict["data"] = self.field_excluder.remove_fields(
                        finding_dict.get("data") or {}
                    )
                results.append(finding_dict)
                continue

            finding_summary = {
                "id": f.id,
                "status": f.status,
            }
            # get_findings() returns FindingRaw objects whose data attributes are
            # already raw scalars (str/list), so we read them directly.
            for field_name in ["title", "cvss", "severity"]:
                if hasattr(f.data, field_name):
                    finding_summary[field_name] = getattr(f.data, field_name)

            # Apply field exclusion to summary if configured
            if self.field_excluder:
                finding_summary = self.field_excluder.remove_fields(finding_summary)

            results.append(finding_summary)

        results = self._apply_limit(results, limit)
        self._log(f"list_findings returning {len(results)} findings")
        return results

    def list_templates(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lists all finding templates from the library (summary).

        Args:
            limit: Maximum number of templates to return. ``None`` returns all.
                Must be a positive integer; non-positive values raise ``ValueError``.
        """
        self._log("list_templates called")
        with self._wrap_api_errors():
            templates = self.reptor.api.templates.search()
        results = []
        for t in templates:
            results.append(
                {
                    "id": t.id,
                    "title": t.get_main_title(),
                    "source": t.source.value
                    if hasattr(t.source, "value")
                    else str(t.source),
                    "tags": t.tags,
                }
            )
        results = self._apply_limit(results, limit)
        self._log(f"list_templates returning {len(results)} templates summary")
        return results

    def get_finding(self, finding_id: str) -> Dict[str, Any]:
        """Retrieves a single finding with field exclusion.

        Args:
            finding_id: The ID of the finding to retrieve.
        """
        self._log(f"get_finding called for id: {finding_id}")

        self._ensure_project()

        with self._wrap_api_errors():
            finding = self.reptor.api.projects.get_finding(finding_id)
        finding_dict = finding.to_dict()

        if self.field_excluder:
            finding_dict["data"] = self.field_excluder.remove_fields(
                finding_dict["data"]
            )
        self._log(f"get_finding returning: {finding_dict}")

        return finding_dict

    def create_finding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new finding.

        Note: Field exclusion is NOT applied on write operations. Excluded fields
        included in the input data are silently ignored (not written to API).

        Args:
            data: The finding data.
                Vulnerability fields (title, description, affected_components, cvss, etc.)
                MUST be provided at the top level of this dict; they will be automatically nested
                into a 'data' object for the SysReptor API.
                Top-level finding fields (status, assignee, language) can also be provided.
        """
        self._log(f"create_finding called with data: {data}")
        self._ensure_project()

        # Prepare API payload
        payload = {}
        vulnerability_data = {}

        for key, value in data.items():
            if key in TOP_LEVEL_FINDING_FIELDS:
                payload[key] = value
            else:
                vulnerability_data[key] = value

        # Remove excluded fields from data being written
        if self.field_excluder:
            vulnerability_data = self.field_excluder.remove_fields(vulnerability_data)

        payload["data"] = vulnerability_data

        with self._wrap_api_errors():
            finding = self.reptor.api.projects.create_finding(payload)
        result = finding.to_dict()

        # Apply field exclusion to result for consistency
        if self.field_excluder:
            result["data"] = self.field_excluder.remove_fields(result["data"])
        self._log(f"create_finding returning: {result}")

        return result

    def delete_finding(self, finding_id: str):
        """Deletes a finding.

        Args:
            finding_id: The ID of the finding to delete.
        """
        self._log(f"delete_finding called for {finding_id}")

        self._ensure_project()

        with self._wrap_api_errors():
            self.reptor.api.projects.delete_finding(finding_id)

    def patch_finding(
        self, finding_id: str, field_name: str, field_value: Any
    ) -> Dict[str, Any]:
        """Patches a single field on a finding.

        This method implements the MCP single-field update workflow:
        1. Constructs a partial payload with only the specified field
        2. Auto-nests data fields into a "data" object
        3. Sends partial payload to API without fetching current finding
        4. API validates, merges, and returns updated finding

        Note: Field exclusion is NOT applied on write operations. The API
        validates field types and ignores unknown fields. API errors are
        enriched with the server's response body (see ``_wrap_api_errors``) so
        the caller can see *why* a write was rejected.

        Args:
            finding_id: The ID of the finding to update.
            field_name: The name of the field to update (e.g., "title", "status").
            field_value: The new value for the field.

        Returns:
            Updated finding data from API response.

        Raises:
            ValueError: If no project is configured.
            HTTPError: If the API returns an error (enriched with the response body).
        """
        self._log(
            f"patch_finding called for {finding_id}, field: {field_name}, value: {field_value}"
        )

        self._ensure_project()

        # Construct partial payload based on field classification
        if field_name in TOP_LEVEL_FINDING_FIELDS:
            payload = {field_name: field_value}
        else:
            # Auto-nest data fields into "data" object
            payload = {"data": {field_name: field_value}}

        # Send partial payload to API (no fetching, no client-side validation)
        with self._wrap_api_errors():
            finding = self.reptor.api.projects.update_finding(finding_id, payload)
        result = finding.to_dict()

        # Apply field exclusion to result for consistency
        if self.field_excluder:
            result["data"] = self.field_excluder.remove_fields(result["data"])

        self._log(f"patch_finding returning: {result}")
        return result

    def search_templates(
        self, query: str = "", limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Searches finding templates (summary).

        Args:
            query: The search term to find templates.
            limit: Maximum number of templates to return. ``None`` returns all.
                Must be a positive integer; non-positive values raise ``ValueError``.
        """
        self._log(f"search_templates called with query: '{query}'")
        with self._wrap_api_errors():
            templates = self.reptor.api.templates.search(query)
        results = []
        for t in templates:
            results.append(
                {
                    "id": t.id,
                    "title": t.get_main_title(),
                    "source": t.source.value
                    if hasattr(t.source, "value")
                    else str(t.source),
                    "tags": t.tags,
                }
            )
        return self._apply_limit(results, limit)

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Gets a finding template by ID.

        Args:
            template_id: The ID of the template to retrieve.
        """
        self._log(f"get_template called for {template_id}")
        with self._wrap_api_errors():
            template = self.reptor.api.templates.get_template(template_id)
        return template.to_dict()

    def list_notes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lists notes for the configured project (summary).

        Returns a navigational summary of each note (id, title, parent, order,
        checked, icon) in tree order: siblings sorted by ``order``, children
        grouped under their parents (depth-first). Use ``get_note`` to read the
        full markdown ``text``.

        Args:
            limit: Maximum number of notes to return. ``None`` returns all.
                Must be a positive integer; non-positive values raise ``ValueError``.
        """
        self._log("list_notes called")
        self._ensure_project()
        with self._wrap_api_errors():
            notes = self.reptor.api.notes.get_notes()

        notes = self._order_notes_tree(notes)
        results = []
        for n in notes:
            note_summary = {
                "id": n.id,
                "title": n.title,
                "parent": getattr(n, "parent", None),
                "order": getattr(n, "order", None),
                "checked": getattr(n, "checked", None),
                "icon_emoji": getattr(n, "icon_emoji", None),
            }
            if self.field_excluder:
                note_summary = self.field_excluder.remove_fields(note_summary)
            results.append(note_summary)

        results = self._apply_limit(results, limit)
        self._log(f"list_notes returning {len(results)} notes summary")
        return results

    def get_note(
        self, note_id: Optional[str] = None, title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gets a single note by ID or title, including its full markdown text.

        Args:
            note_id: The ID of the note to retrieve (preferred over title).
            title: The title of the note to retrieve (used if note_id is omitted).

        Raises:
            ValueError: If neither note_id nor title is provided, or no note matches.
        """
        self._log(f"get_note called for id: {note_id}, title: {title}")
        if not note_id and not title:
            raise ValueError("Either note_id or title must be provided.")

        self._ensure_project()
        with self._wrap_api_errors():
            note = self.reptor.api.notes.get_note(id=note_id, title=title)

        if note is None:
            raise ValueError(
                f"Note not found (note_id={note_id!r}, title={title!r})."
            )

        result = note.to_dict()
        if self.field_excluder:
            result = self.field_excluder.remove_fields(result)
        self._log(f"get_note returning: {result}")
        return result

    def write_note(
        self,
        title: Optional[str] = None,
        text: str = "",
        note_id: Optional[str] = None,
        parent_title: Optional[str] = None,
        timestamp: bool = False,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """Creates a note, or appends to / replaces an existing one.

        If ``note_id`` is given, ``text`` is written to that note. Otherwise the
        note is looked up (or created) by ``title``. ``text`` is appended by
        default; pass ``overwrite=True`` to replace the note's content instead.

        Args:
            title: Title of the note to write to / create (required if no note_id).
            text: Markdown text to write to the note.
            note_id: ID of an existing note to write to.
            parent_title: Title of a parent note to nest a newly created note under.
            timestamp: Prepend a timestamp to the inserted text.
            overwrite: Replace the note's existing text instead of appending.

        Raises:
            ValueError: If neither note_id nor title is provided.
        """
        self._log(
            f"write_note called for id: {note_id}, title: {title}, "
            f"parent: {parent_title}, overwrite: {overwrite}"
        )
        if not note_id and not title:
            raise ValueError("Either note_id or title must be provided.")

        self._ensure_project()
        with self._wrap_api_errors():
            written = self.reptor.api.notes.write_note(
                id=note_id,
                title=title,
                text=text,
                parent_title=parent_title,
                timestamp=timestamp,
                overwrite=overwrite,
            )

        if written is None:
            return {"status": "written", "note_id": note_id, "title": title}
        result = written.to_dict()
        if self.field_excluder:
            result = self.field_excluder.remove_fields(result)
        self._log(f"write_note returning: {result}")
        return result

    def _simplify_field(self, field) -> Dict[str, Any]:
        """Convert a ProjectDesignField to a simplified dict."""
        field_type = (
            field.type.value if hasattr(field.type, "value") else str(field.type)
        )
        field_info: Dict[str, Any] = {
            "id": field.id,
            "type": field_type,
            "label": field.label,
            "required": field.required,
        }
        # Include choices for enum fields
        if field_type == "enum" and field.choices:
            field_info["choices"] = [
                c.get("value") for c in field.choices if c.get("value")
            ]
        # Include items for list fields (recursively simplify if it's a ProjectDesignField)
        if field_type == "list" and field.items:
            if hasattr(field.items, "id"):
                field_info["items"] = self._simplify_field(field.items)
            else:
                field_info["items"] = field.items
        # Include properties for object fields (recursively simplify)
        if field_type == "object" and field.properties:
            field_info["properties"] = [
                self._simplify_field(p) for p in field.properties
            ]
        return field_info

    def get_finding_schema(self) -> Dict[str, Any]:
        """Gets the finding field schema for the configured project.

        This is a convenience method that fetches the project's design and returns
        a simplified schema of finding fields, making it easier to understand
        what fields are available and their types.

        Returns:
            A dict containing project_id, project_type, and finding_fields with
            simplified field definitions (id, type, label, required, choices, items, properties).
        """
        project_id = self._ensure_project()
        self._log(f"get_finding_schema called for project {project_id}")

        with self._wrap_api_errors():
            project = self.reptor.api.projects.project
            design = self.reptor.api.project_designs.get_project_design(
                project.project_type
            )

        return {
            "project_id": project_id,
            "project_type": project.project_type,
            "finding_fields": [self._simplify_field(f) for f in design.finding_fields],
        }

    def get_project_schema(self) -> Dict[str, Any]:
        """Gets the report field schema for the configured project.

        This is a convenience method that fetches the project's design and returns
        a simplified schema of report fields, making it easier to understand
        what report sections and fields are available and their types.

        Returns:
            A dict containing project_id, project_type, and report_fields with
            simplified field definitions (id, type, label, required, choices, items, properties).
        """
        project_id = self._ensure_project()
        self._log(f"get_project_schema called for project {project_id}")

        with self._wrap_api_errors():
            project = self.reptor.api.projects.project
            design = self.reptor.api.project_designs.get_project_design(
                project.project_type
            )

        return {
            "project_id": project_id,
            "project_type": project.project_type,
            "report_fields": [self._simplify_field(f) for f in design.report_fields],
        }

    def list_sections(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lists all report sections for the configured project.

        Returns a simplified list of sections with metadata (id, type, label)
        for each section. This provides a high-level overview without sensitive
        section data content.

        Args:
            limit: Maximum number of sections to return. ``None`` returns all.
                Must be a positive integer; non-positive values raise ``ValueError``.

        Returns:
            List of section metadata dictionaries containing:
            - id: Section ID (e.g., "executive_summary")
            - type: Section type (e.g., "section")
            - label: Human-readable label (e.g., "Executive Summary")
        """
        self._log("list_sections called")
        self._ensure_project()
        with self._wrap_api_errors():
            sections = self.reptor.api.projects.get_sections()

        results = []
        for section in sections:
            section_info = {
                "id": section.id,
                "type": "section",
                "label": section.label,
            }

            # Apply field exclusion if configured
            if self.field_excluder:
                section_info = self.field_excluder.remove_fields(section_info)

            results.append(section_info)

        results = self._apply_limit(results, limit)
        self._log(f"list_sections returning {len(results)} sections")
        return results

    def get_section(self, section_id: str) -> Dict[str, Any]:
        """Retrieves a single section by ID with field exclusion.

        Args:
            section_id: The ID of the section to retrieve.

        Returns:
            Section data dictionary with field exclusion applied.
        """
        self._log(f"get_section called for id: {section_id}")

        self._ensure_project()

        with self._wrap_api_errors():
            sections = self.reptor.api.projects.get_sections()

        # Find the section with matching ID
        section = None
        for s in sections:
            if s.id == section_id:
                section = s
                break

        if section is None:
            raise ValueError(f"Section with id '{section_id}' not found")

        # Convert section to dictionary
        section_dict = section.to_dict()

        # Apply field exclusion to section data if configured
        if self.field_excluder and "data" in section_dict:
            section_dict["data"] = self.field_excluder.remove_fields(
                section_dict["data"]
            )

        self._log(f"get_section returning: {section_dict}")
        return section_dict

    def patch_project_data(
        self, section_id: str, field_id: str, value: Any
    ) -> Dict[str, Any]:
        """Patches a single field in a section's data.

        This method implements the MCP single-field update workflow:
        1. Constructs a partial payload with only the specified field
        2. Sends partial payload to API without fetching current section
        3. API validates, merges, and returns updated section
        4. Returns updated section data with FieldExcluder filtering

        Args:
            section_id: The ID of the section to update (e.g., "executive_summary").
            field_id: The ID of the field to update within section.data.
            value: The new value for the field.

        Returns:
            Updated section data from API response with FieldExcluder filtering applied.

        Raises:
            ValueError: If no project is configured.
            HTTPError: If the API returns an error (enriched with the response body).
        """
        self._log(
            f"patch_project_data called for section: {section_id}, field: {field_id}, value: {value}"
        )

        self._ensure_project()

        # Send partial update (consistent with patch_finding pattern)
        section_data = {"data": {field_id: value}}
        with self._wrap_api_errors():
            updated_section_raw = self.reptor.api.projects.update_section(
                section_id, section_data
            )

        # Convert to dict and apply FieldExcluder filtering
        updated_section = updated_section_raw.to_dict()
        if self.field_excluder and "data" in updated_section:
            updated_section["data"] = self.field_excluder.remove_fields(
                updated_section["data"]
            )

        self._log(f"patch_project_data returning: {updated_section}")
        return updated_section
