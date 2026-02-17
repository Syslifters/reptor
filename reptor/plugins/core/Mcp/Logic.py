from typing import Optional, List, Any, Dict


class McpLogic:
    """
    Business logic for MCP operations, decoupling SysReptor API interactions
    from the MCP transport layer.
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

    def _log(self, msg: str):
        if self.logger:
            self.logger.debug(f"{msg}")

    def _get_project_id(self) -> str:
        """Get the configured project ID"""
        project_id = self.reptor.get_active_project_id()
        if not project_id:
            raise ValueError(
                "No project configured. Set project_id via 'reptor conf', "
                "environment variable REPTOR_PROJECT_ID, or --project-id flag."
            )
        return project_id

    def list_findings(self) -> List[Dict[str, Any]]:
        """Lists all findings for the configured project (summary)."""
        self._log("list_findings called")
        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)
        findings_raw = self.reptor.api.projects.get_findings()

        results = []
        for f in findings_raw:
            finding_summary = {
                "id": f.id,
                "status": f.status,
            }
            for field_name in ["title", "cvss"]:
                if hasattr(f.data, field_name):
                    field_obj = getattr(f.data, field_name)
                    if field_obj is not None and hasattr(field_obj, "value"):
                        finding_summary[field_name] = field_obj.value
                    else:
                        finding_summary[field_name] = field_obj

            # Apply field exclusion to summary if configured
            if self.field_excluder:
                finding_summary = self.field_excluder.remove_fields(finding_summary)

            results.append(finding_summary)
        self._log(f"list_findings returning {len(results)} findings summary")
        return results

    def list_templates(self) -> List[Dict[str, Any]]:
        """Lists all finding templates from the library (summary)."""
        self._log("list_templates called")
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
        self._log(f"list_templates returning {len(results)} templates summary")
        return results

    def get_finding(self, finding_id: str) -> Dict[str, Any]:
        """Retrieves a single finding with field exclusion.

        Args:
            finding_id: The ID of the finding to retrieve.
        """
        self._log(f"get_finding called for id: {finding_id}")

        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

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
        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

        # Prepare API payload
        payload = {}
        vulnerability_data = {}

        # Define fields that stay at the top level
        top_level_fields = ["status", "assignee", "language", "template", "order"]

        for key, value in data.items():
            if key in top_level_fields:
                payload[key] = value
            else:
                vulnerability_data[key] = value

        # Remove excluded fields from data being written
        if self.field_excluder:
            vulnerability_data = self.field_excluder.remove_fields(vulnerability_data)

        payload["data"] = vulnerability_data

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

        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

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
        validates field types and ignores unknown fields per Decision 3.
        API errors are propagated without modification per Decision 4.

        Args:
            finding_id: The ID of the finding to update.
            field_name: The name of the field to update (e.g., "title", "status").
            field_value: The new value for the field.

        Returns:
            Updated finding data from API response.

        Raises:
            ValueError: If no project is configured.
            HTTPError: If the API returns an error (propagated without modification).
        """
        self._log(
            f"patch_finding called for {finding_id}, field: {field_name}, value: {field_value}"
        )

        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

        # Field classification: top-level vs data fields (nested in "data")
        top_level_fields = [
            "status",
            "assignee",
            "language",
            "template",
            "order",
        ]

        # Construct partial payload based on field classification
        if field_name in top_level_fields:
            payload = {field_name: field_value}
        else:
            # Auto-nest data fields into "data" object
            payload = {"data": {field_name: field_value}}

        # Send partial payload to API (no fetching, no client-side validation)
        finding = self.reptor.api.projects.update_finding(finding_id, payload)
        result = finding.to_dict()

        # Apply field exclusion to result for consistency
        if self.field_excluder:
            result["data"] = self.field_excluder.remove_fields(result["data"])

        self._log(f"patch_finding returning: {result}")
        return result

    def search_templates(self, query: str = "") -> List[Dict[str, Any]]:
        """Searches finding templates (summary).

        Args:
            query: The search term to find templates.
        """
        self._log(f"search_templates called with query: '{query}'")
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
        return results

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Gets a finding template by ID.

        Args:
            template_id: The ID of the template to retrieve.
        """
        self._log(f"get_template called for {template_id}")
        template = self.reptor.api.templates.get_template(template_id)
        return template.to_dict()

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
        project_id = self._get_project_id()
        self._log(f"get_finding_schema called for project {project_id}")
        self.reptor.api.projects.init_project(project_id)

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
        project_id = self._get_project_id()
        self._log(f"get_project_schema called for project {project_id}")
        self.reptor.api.projects.init_project(project_id)

        project = self.reptor.api.projects.project
        design = self.reptor.api.project_designs.get_project_design(
            project.project_type
        )

        return {
            "project_id": project_id,
            "project_type": project.project_type,
            "report_fields": [self._simplify_field(f) for f in design.report_fields],
        }

    def list_sections(self) -> List[Dict[str, Any]]:
        """Lists all report sections for the configured project.

        Returns a simplified list of sections with metadata (id, type, label)
        for each section. This provides a high-level overview without sensitive
        section data content.

        Returns:
            List of section metadata dictionaries containing:
            - id: Section ID (e.g., "executive_summary")
            - type: Section type (e.g., "section")
            - label: Human-readable label (e.g., "Executive Summary")
        """
        self._log("list_sections called")
        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)
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

        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

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
            HTTPError: If the API returns an error (propagated without modification).
        """
        self._log(
            f"patch_project_data called for section: {section_id}, field: {field_id}, value: {value}"
        )

        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

        # Send partial update (consistent with patch_finding pattern)
        section_data = {"data": {field_id: value}}
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
