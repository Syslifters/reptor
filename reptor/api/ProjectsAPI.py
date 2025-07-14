import typing
from contextlib import contextmanager
from functools import cached_property
from posixpath import join as urljoin

from requests import HTTPError

from reptor.api.APIClient import APIClient
from reptor.models.Finding import FindingRaw
from reptor.models.Project import Project, ProjectOverview
from reptor.models.ProjectDesign import ProjectDesign
from reptor.models.Section import Section, SectionRaw


class ProjectsAPI(APIClient):
    """API client for interacting with SysReptor projects.

    Example:
        ```python
        from reptor import Reptor

        reptor = Reptor(
            server=os.environ.get("REPTOR_SERVER"),
            token=os.environ.get("REPTOR_TOKEN"),
            project_id="41c09e60-44f1-453b-98f3-3f1875fe90fe",
        )

        # ProjectsAPI is available as reptor.api.projects, e.g.:
        reptor.api.projects.fetch_project()
        ```
    """
    
    # Initialization & Configuration
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._init_attrs()

    def _init_attrs(self) -> None:
        self.project_design = None

        if not (server := self.reptor.get_config().get_server()):
            raise ValueError("No SysReptor server configured. Try 'reptor conf'.")

        self.base_endpoint = f"{server}/api/v1/pentestprojects"
        self.debug(self.base_endpoint)

    @property
    def object_endpoint(self) -> str:
        return urljoin(self.base_endpoint, self.project_id)

    def search(self, search_term: typing.Optional[str] = "", finished: typing.Optional[bool] = None) -> typing.List[ProjectOverview]:
        """Searches projects by search term and retrieves all projects that match.

        Args:
            search_term (typing.Optional[str], optional): Search Term to look for. Defaults to None.
            finished (bool, optional): Filter for (un)finished projects. Defaults to None.

        Returns:
            List of project overviews (without sections, findings) that match
        
        Example:
            ```python
            projects = reptor.api.projects.search()
            ```
        """
        params={"search": search_term}
        if finished is not None:
            params["readonly"] = finished
        projects_raw = self.get_paginated(self.base_endpoint, params=params)
        return [ProjectOverview(project_raw) for project_raw in projects_raw]

    def check_report(self, group_messages=False) -> dict:
        url = urljoin(self.base_endpoint, f"{self.project_id}/check")
        data = self.get(url).json()
        if group_messages:
            data = data.get("messages")
            # data is a list of dicts. group by "message" key
            grouped = dict()
            for item in data:
                grouped.setdefault(item["message"], []).append(item)
            """
            {
              "Empty field": [
                {
                  "level": "warning",
                  "message": "Empty field",
                  "details": null,
                  "location": {
                      "type": "section",
                      "id": "other",
                      "name": "General",
                      "path": "report_date"
                  }
                }
              ]
            }
            """
            return grouped
        """
        {
          "messages": [
            {
              "level": "warning",
              "message": "Empty field",
              "details": null,
              "location": {
                  "type": "section",
                  "id": "other",
                  "name": "General",
                  "path": "report_date"
              }
            }
          ]
        }
        """
        return data

    def get_enabled_language_codes(self) -> list:
        url = urljoin(self.reptor.get_config().get_server(), "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            language["code"] for language in settings.get("languages", list()) if language["enabled"] is True
        ]
        return languages

    def init_project(self, new_project_id) -> None:
        """Switches the current project context to a new project ID.
        
        Args:
            new_project_id (str): Project ID to switch to.
        
        Example:
            ```python
            reptor.api.projects.init_project("41c09e60-44f1-453b-98f3-3f1875fe90fe")
            ```
        """
        self.reptor._config._raw_config["project_id"] = new_project_id
        self._project_id = new_project_id
        self._init_attrs()
        self.reptor._api = None

    # Project Lifecycle Management
    def create_project(
        self,
        name: str,
        project_design: str,
        tags: typing.Optional[typing.List[str]] = None,
    ) -> Project:
        """Creates a new project in SysReptor.

        Args:
            name (str): Project name
            project_design (str): Project Design ID
            tags (List[str] | None, optional): Project tags, defaults to None.
        
        Returns:
            Project object of the newly created project.
        
        Example:
            ```python
            project = reptor.api.projects.create_project(
                name="My New Project",
                project_design="081e2b21-cc41-4ade-8987-e75417cac76b",
                tags=["webapp", "ticket-3321"]
            )
            ```
        """
        data = {
            "name": name,
            "project_type": project_design,
            "tags": tags or list(),
        }
        return Project(self.post(self.base_endpoint, json=data).json(), ProjectDesign())

    def duplicate_project(self, project_id: typing.Optional[str] = None) -> Project:
        """Duplicates a project in SysReptor.

        Args:
            project_id (str, optional): Project ID to duplicate. If None, duplicates current project. Defaults to None.

        Returns:
            Project object of the duplicated project.
        
        Example:
            ```python
            # Duplicate current project
            duplicated_project = reptor.api.projects.duplicate_project()
            print(f"Duplicated to project ID: {duplicated_project.id}")
            
            # Duplicate specific project
            duplicated_project = reptor.api.projects.duplicate_project("41c09e60-44f1-453b-98f3-3f1875fe90fe")
            ```
        """
        url = urljoin(self.base_endpoint, f"{project_id or self.project_id}/copy/")
        duplicated_project = self.post(url).json()
        return Project(
            duplicated_project,
            self.reptor.api.project_designs.project_design,
        )

    @contextmanager
    def duplicate_and_cleanup(self):
        """Context manager that duplicates current project, switches to it, and cleans up on exit.
        
        Returns:
            Context manager for temporary project operations.
        
        Example:
            ```python
            with reptor.api.projects.duplicate_and_cleanup():
                # Work with duplicated project
                reptor.api.projects.update_project({"name": "Test Project"})
                # Project is automatically deleted when exiting context
            ```
        """
        original_project_id = self.project_id
        duplicated_project = self.duplicate_project()
        self.init_project(duplicated_project.id)
        self.log.info(f"Duplicated project to {duplicated_project.id}")

        yield

        self.delete_project()
        self.init_project(original_project_id)
        self.log.info("Cleaned up duplicated project")

    def finish_project(self, project_id: typing.Optional[str] = None, unfinish: bool = False) -> bool:
        """Marks a project as finished (readonly) or unfinished.
        
        Args:
            project_id (str, optional): Project ID to finish. If None, uses current project. Defaults to None.
            unfinish (bool, optional): Marks project as unfinished. Defaults to False.
        
        Returns:
            True if project is readonly/finished, False if unfinished.
        
        Example:
            ```python
            # Finish current project
            is_finished = reptor.api.projects.finish_project()
            
            # Unfinish a specific project
            is_finished = reptor.api.projects.finish_project(
                project_id="41c09e60-44f1-453b-98f3-3f1875fe90fe",
                unfinish=True
            )
            ```
        """
        if project_id:
            url = urljoin(self.base_endpoint, project_id)
        else:
            url = self.object_endpoint
        url = urljoin(url, "readonly/")
        return self.patch(
            url,
            json={"readonly": not unfinish}
        ).json().get("readonly")

    def delete_project(self, project_id: typing.Optional[str] = None) -> None:
        """Deletes a project from SysReptor.
        
        Args:
            project_id (str, optional): Project ID to delete. If None, deletes current project. Defaults to None.
        
        Returns:
            :
        
        Example:
            ```python
            # Delete current project
            reptor.api.projects.delete_project()
            
            # Delete specific project
            reptor.api.projects.delete_project("41c09e60-44f1-453b-98f3-3f1875fe90fe")
            ```
        """
        if project_id:
            url = urljoin(self.base_endpoint, project_id)
        else:
            url = self.object_endpoint
        self.delete(url)

    # Project Data Operations
    @cached_property
    def project(self) -> Project:
        return self.fetch_project()

    @cached_property
    def _project_dict(self) -> dict:
        return self._fetch_project_dict()
    
    def _fetch_project_dict(self, html=False) -> dict:
        """Fetches the project dictionary from the API"""
        if html:
            url = urljoin(self.base_endpoint, f"{self.project_id}/md2html/")
            return self.post(url).json()
        else:
            url = self.object_endpoint
            return self.get(url).json()

    def fetch_project(self, html=False) -> Project:
        return Project(
            self._fetch_project_dict(html=html),
            self.reptor.api.project_designs.project_design,
        )

    def update_project(self, data: dict) -> Project:
        """Updates project metadata.
        
        Args:
            data (dict): Project data to update (name, tags, etc.).
        
        Returns:
            Updated project object.
        
        Example:
            ```python
            updated_project = reptor.api.projects.update_project({
                "name": "Updated Project Name",
                "tags": ["webapp", "internal"]
            })
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        return Project(
            self.patch(url, json=data).json(),
            self.reptor.api.project_designs.project_design,
        )

    def update_project_design(self, design_id, force=False) -> Project:
        """Updates the project design (template) of the current project.
        
        Args:
            design_id (str): ID of the new project design.
            force (bool, optional): Force change even if designs are incompatible (might lead to data loss). Defaults to False.
        
        Returns:
            Updated project object.
        
        Example:
            ```python
            updated_project = reptor.api.projects.update_project_design(
                "b0a54c7d-ca54-4629-bb1d-36d7e5e88bf7",
            )
            ```
        """
        data = {
            "project_type": design_id,
            "force_change_project_type": True if force else False,
        }
        try:
            return self.update_project(data)
        except HTTPError as e:
            raise (HTTPError(e.response.text))

    def export(self) -> bytes:
        """Exports a Project in archive format (tar.gz).
        
        Returns:
            Project archive content.
        
        Example:
            ```python
            project_archive = reptor.api.projects.export()
            with open("project.tar.gz", "wb") as f:
                f.write(project_archive)
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/export/all")
        return self.post(url).content

    def render(self) -> bytes:
        """Renders project to PDF.
        
        Returns:
            PDF content of the project report.

        Example:
            ```python
            my_report = reptor.api.projects.render()
            with open("my_report.pdf", "wb") as f:
                f.write(my_report)
            ```
        """
        # Get report checks
        checks = self.check_report(group_messages=True)
        for check, warnings in checks.items():
            if any([w.get("level") == "warning" for w in warnings]):
                self.log.warning(f'Report Check Warning: "{check}" (x{len(warnings)})')

        # Render report
        url = urljoin(self.base_endpoint, f"{self.project_id}/generate/")
        try:
            return self.post(url).content
        except HTTPError as e:
            try:
                for msg in e.response.json().get("messages", []):
                    if msg.get("level") == "error":
                        self.log.error(msg.get("message"))
                    elif msg.get("level") == "warning":
                        self.log.warning(msg.get("message"))
            except Exception:
                pass
            raise e

    # Section Operations
    def get_sections(self) -> typing.List[Section]:
        """Gets all sections of the current project.

        Returns:
            List of sections for this project.
        
        Example:
            ```python
            sections = reptor.api.projects.get_sections()
            ```
        """
        return_data = list()
        url = urljoin(self.base_endpoint, f"{self.project_id}/sections/")
        response = self.get(url).json()

        if not response:
            return return_data

        if not self.project_design:
            self.project_design = self.reptor.api.project_designs.project_design

        for item in response:
            section = Section(SectionRaw(item), self.project_design)
            return_data.append(section)
        return return_data

    def update_section(self, section_id: str, data: dict) -> SectionRaw:
        """Updates a section with new data.
        
        Args:
            section_id (str): ID of the section to update.
            data (dict): Section data to update.
        
        Returns:
            Updated section object.
        
        Example:
            ```python
            updated_section = reptor.api.projects.update_section(
                "other",
                {"data": {"report_date": "2024-01-15"}}
            )
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/sections/{section_id}/")
        return SectionRaw(self.patch(url, json=data).json())

    def update_sections(self, sections: typing.List[dict]) -> typing.List[SectionRaw]:
        """Updates multiple sections with new data.
        
        Args:
            sections (typing.List[dict]): List of section data dictionaries to update.
        
        Returns:
            List of updated section objects.
        
        Example:
            ```python
            updated_sections = reptor.api.projects.update_sections([
                {"id": "other", "data": {"report_date": "2024-01-15"}},
                {"id": "executive_summary", "data": {"summary": "Updated summary"}}
            ])
            ```
        """
        project_design = self.reptor.api.project_designs.project_design
        updated_sections = list()
        for section_data in sections:
            Section(
                section_data,
                project_design,
                strict_type_check=False,
            )  # Raises ValueError if invalid
            if not section_data.get("id"):
                raise ValueError("Section data must contain an 'id' field.")
        for section_data in sections:
            # Iterate a second time to check that all sections are valid
            updated_sections.append(self.update_section(section_data.get("id"), section_data))
        return updated_sections

    def update_report_fields(self, data: dict) -> typing.List[SectionRaw]:
        self.log.warning(
            "update_report_fields() is deprecated and will be removed in a future version. "
            "Use update_sections() instead for more reliable field updates."
        )
        # Get project data to map report fields to sections
        project = self.reptor.api.projects.project
        project_design = self.reptor.api.project_designs.project_design
        # Map fields to sections
        sections_data = dict()
        for section in project.sections:
            sections_data[section.id] = {"data": {}}
            for report_field_name, report_field_data in data.items():
                if report_field_name in section.fields:
                    sections_data[section.id]["data"][
                        report_field_name
                    ] = report_field_data

        # Check for valid report field data format
        for _, section_data in sections_data.items():
            Section(
                section_data,
                project_design,
                strict_type_check=False,
            )  # Raises ValueError if invalid

        # Upload
        sections = list()
        for section_id, section_data in sections_data.items():
            if section_data["data"]:
                sections.append(self.update_section(section_id, section_data))
        return sections

    # Finding Operations
    def get_findings(self) -> typing.List[FindingRaw]:
        """Gets all findings of the current project.

        Returns:
            List of findings for this project.
        
        Example:
            ```python
            findings = reptor.api.projects.get_findings()
            for finding in findings:
                print(f"Finding: {finding.data.get('title', 'Untitled')}")
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url).json()

        if not response:
            return []
        return [FindingRaw(f) for f in response]

    def get_finding(self, finding_id: str) -> FindingRaw:
        """Gets a single finding by ID.

        Args:
            finding_id (str): ID of the finding to retrieve.

        Returns:
            Finding object.
        
        Example:
            ```python
            finding = reptor.api.projects.get_finding("3294a042-0ab6-4463-a95d-1915561d2820")
            print(finding.data.get('title'))
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        return FindingRaw(self.get(url).json())

    def create_finding(self, data: dict) -> FindingRaw:
        """Creates a new finding in the current project.
        
        Args:
            data (dict): Finding data for the new finding.
        
        Returns:
            Created finding object.
        
        Example:
            ```python
            new_finding = reptor.api.projects.create_finding({
                "title": "SQL Injection",
                "severity": "high",
                "description": "Found SQL injection vulnerability..."
            })
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        return FindingRaw(self.post(url, json=data).json())

    def create_finding_from_template(self, template_id: str, language: typing.Optional[str] = None) -> FindingRaw:
        """Creates a new finding from a template.
        
        Args:
            template_id (str): Finding template ID.
            language (str, optional): Language code for the template. Defaults to None.
        
        Returns:
            Created finding object.
        
        Example:
            ```python
            finding = reptor.api.projects.create_finding_from_template(
                "38cbd644-c83c-4157-a27c-df3ee9472f92",
                language="en-US"
            )
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/fromtemplate/")
        data = {"template": template_id}
        if language:
            data["template_language"] = language
        return FindingRaw(self.post(url, json=data).json())

    def update_finding(self, finding_id: str, data: dict) -> FindingRaw:
        """Updates an existing finding with new data.
        
        Args:
            finding_id (str): ID of the finding to update.
            data (dict): Finding data to update.
        
        Returns:
            Updated finding object.
        
        Example:
            ```python
            updated_finding = reptor.api.projects.update_finding(
                "3294a042-0ab6-4463-a95d-1915561d2820",
                {"title": "Updated Title", "severity": "high"}
            )
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        return FindingRaw(self.patch(url, json=data).json())

    def delete_finding(self, finding_id: str) -> None:
        """Deletes a finding from the current project.
        
        Args:
            finding_id (str): ID of the finding to delete.
        
        Returns:
            :
        
        Example:
            ```python
            reptor.api.projects.delete_finding("finding-uuid-here")
            ```
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        self.delete(url)
