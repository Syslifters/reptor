from typing import Optional, List, Any, Dict

class McpLogic:
    """
    Business logic for MCP operations, decoupling SysReptor API interactions
    from the MCP transport layer.
    """
    def __init__(self, reptor_instance: Any, anonymizer: Optional[Any] = None, logger: Optional[Any] = None):
        self.reptor = reptor_instance
        self.anonymizer = anonymizer
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
            
            results.append(finding_summary)
        self._log(f"list_findings returning {len(results)} findings summary")
        return results

    def list_templates(self) -> List[Dict[str, Any]]:
        """Lists all finding templates from the library (summary)."""
        self._log("list_templates called")
        templates = self.reptor.api.templates.search()
        results = []
        for t in templates:
            results.append({
                "id": t.id,
                "title": t.get_main_title(),
                "source": t.source.value if hasattr(t.source, "value") else str(t.source),
                "tags": t.tags
            })
        self._log(f"list_templates returning {len(results)} templates summary")
        return results


    def get_finding(self, finding_id: str) -> Dict[str, Any]:
        """Retrieves a single finding with anonymization.

        Args:
            finding_id: The ID of the finding to retrieve.
        """
        self._log(f"get_finding called for id: {finding_id}")

        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

        finding = self.reptor.api.projects.get_finding(finding_id)
        finding_dict = finding.to_dict()

        if self.anonymizer:
            finding_dict["data"] = self.anonymizer.anonymize(project_id, finding_dict["data"])
        self._log(f"get_finding returning: {finding_dict}")

        return finding_dict

    def create_finding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new finding, handling de-anonymization.

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

        if self.anonymizer:
            vulnerability_data = self.anonymizer.deanonymize(project_id, vulnerability_data)

        payload["data"] = vulnerability_data

        finding = self.reptor.api.projects.create_finding(payload)
        result = finding.to_dict()

        if self.anonymizer:
            result["data"] = self.anonymizer.anonymize(project_id, result["data"])
        self._log(f"create_finding returning: {result}")

        return result

    def update_finding(self, finding_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing finding, handling de-anonymization.

        Args:
            finding_id: The ID of the finding to update.
            data: The updated finding data fields.
                Vulnerability fields will be automatically nested into a 'data' object.
        """
        self._log(f"update_finding called for {finding_id} with data: {data}")
        project_id = self._get_project_id()
        self.reptor.api.projects.init_project(project_id)

        # Handle explicit nesting (e.g. from get_finding output)
        if "data" in data and isinstance(data["data"], dict):
            if self.anonymizer:
                data["data"] = self.anonymizer.deanonymize(project_id, data["data"])
            payload = data
        else:
            # Handle flat structure (similar to create_finding)
            payload = {}
            vulnerability_data = {}

            # Define fields that stay at the top level
            top_level_fields = ["status", "assignee", "language", "template", "order"]

            for key, value in data.items():
                if key in top_level_fields:
                    payload[key] = value
                else:
                    vulnerability_data[key] = value

            if self.anonymizer:
                vulnerability_data = self.anonymizer.deanonymize(project_id, vulnerability_data)

            payload["data"] = vulnerability_data

        finding = self.reptor.api.projects.update_finding(finding_id, payload)
        result = finding.to_dict()
        if self.anonymizer:
            result["data"] = self.anonymizer.anonymize(project_id, result["data"])
        self._log(f"update_finding returning: {result}")
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

    def search_templates(self, query: str = "") -> List[Dict[str, Any]]:
        """Searches finding templates (summary).

        Args:
            query: The search term to find templates.
        """
        self._log(f"search_templates called with query: '{query}'")
        templates = self.reptor.api.templates.search(query)
        results = []
        for t in templates:
            results.append({
                "id": t.id,
                "title": t.get_main_title(),
                "source": t.source.value if hasattr(t.source, "value") else str(t.source),
                "tags": t.tags
            })
        return results

    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Gets a finding template by ID.

        Args:
            template_id: The ID of the template to retrieve.
        """
        self._log(f"get_template called for {template_id}")
        template = self.reptor.api.templates.get_template(template_id)
        return template.to_dict()

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
        design = self.reptor.api.project_designs.fetch_project_design(project.project_type)

        def simplify_field(field) -> Dict[str, Any]:
            """Convert a ProjectDesignField to a simplified dict."""
            field_type = field.type.value if hasattr(field.type, 'value') else str(field.type)
            field_info: Dict[str, Any] = {
                "id": field.id,
                "type": field_type,
                "label": field.label,
                "required": field.required,
            }
            # Include choices for enum fields
            if field_type == "enum" and field.choices:
                field_info["choices"] = [c.get("value") for c in field.choices if c.get("value")]
            # Include items for list fields (recursively simplify if it's a ProjectDesignField)
            if field_type == "list" and field.items:
                if hasattr(field.items, 'id'):
                    field_info["items"] = simplify_field(field.items)
                else:
                    field_info["items"] = field.items
            # Include properties for object fields (recursively simplify)
            if field_type == "object" and field.properties:
                field_info["properties"] = [simplify_field(p) for p in field.properties]
            return field_info

        return {
            "project_id": project_id,
            "project_type": project.project_type,
            "finding_fields": [simplify_field(f) for f in design.finding_fields]
        }
