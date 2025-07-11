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

    def create_project(
        self,
        name: str,
        project_design: str,
        tags: typing.Optional[typing.List[str]] = None,
    ) -> Project:
        data = {
            "name": name,
            "project_type": project_design,
            "tags": tags or list(),
        }
        return Project(self.post(self.base_endpoint, json=data).json(), ProjectDesign())

    def search(self, search_term: typing.Optional[str] = "", finished: typing.Optional[bool] = None) -> typing.List[ProjectOverview]:
        """Searches projects by search term and retrieves all projects that match

        Args:
            search_term (typing.Optional[str], optional): Search Term to look for. Defaults to None.
            finished (bool, optional): Filter for (un)finished projects. Defaults to None.

        Returns:
            typing.List[ProjectOverview]: List of project overviews (without sections, findings) that match search
        """
        params={"search": search_term}
        if finished is not None:
            params["readonly"] = finished
        projects_raw = self.get_paginated(self.base_endpoint, params=params)
        return [ProjectOverview(project_raw) for project_raw in projects_raw]

    @cached_property
    def project(self) -> Project:
        return self._get_project()

    @cached_property
    def _project_dict(self) -> dict:
        url = self.object_endpoint
        return self.get(url).json()

    def _get_project(self) -> Project:
        return Project(
            self._project_dict,
            self.reptor.api.project_designs.project_design,
        )

    def export(self) -> bytes:
        """Exports a Project in archive format (tar.gz)"""
        url = urljoin(self.base_endpoint, f"{self.project_id}/export/all")
        return self.post(url).content

    def render(self) -> bytes:
        """Renders project to PDF"""
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

    def check_report(self, group_messages=False) -> dict:
        url = urljoin(self.base_endpoint, f"{self.project_id}/check")
        data = self.get(url).json()
        if group_messages:
            data = data.get("messages")
            # data is a list of dicts. group by "message" key
            grouped = dict()
            for item in data:
                grouped.setdefault(item["message"], []).append(item)
            return grouped
        return data

    def finish_project(self, project_id: typing.Optional[str] = None, unfinish: bool = False) -> bool:
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
        if project_id:
            url = urljoin(self.base_endpoint, project_id)
        else:
            url = self.object_endpoint
        self.delete(url)

    def duplicate_project(self) -> Project:
        """Duplicates Projects

        Returns:
            Project: Project Object
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/copy/")
        duplicated_project = self.post(url).json()
        return Project(
            duplicated_project,
            self.reptor.api.project_designs.project_design,
        )

    @contextmanager
    def duplicate_and_cleanup(self):
        original_project_id = self.project_id
        duplicated_project = self.duplicate_project()
        self.switch_project(duplicated_project.id)
        self.log.info(f"Duplicated project to {duplicated_project.id}")

        yield

        self.delete_project()
        self.switch_project(original_project_id)
        self.log.info("Cleaned up duplicated project")

    def switch_project(self, new_project_id) -> None:
        self.reptor._config._raw_config["project_id"] = new_project_id
        self._project_id = new_project_id
        self._init_attrs()
        self.reptor._api = None

    def get_sections(self) -> typing.List[Section]:
        """Gets all sections of a project

        Returns:
            typing.List[Section]: List of sections for this project
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

    def get_findings(self) -> typing.List[FindingRaw]:
        """Gets all findings of a project

        Returns:
            typing.List[FindingRaw]: List of findings for this project
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url).json()

        if not response:
            return []
        return [FindingRaw(f) for f in response]

    def get_finding(self, finding_id: str) -> FindingRaw:
        """Gets a single finding by ID

        Args:
            finding_id (str): ID of the finding to retrieve

        Returns:
            FindingRaw: Finding object
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        return FindingRaw(self.get(url).json())

    def delete_finding(self, finding_id: str) -> None:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        self.delete(url)

    def update_finding(self, finding_id: str, data: dict) -> FindingRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        return FindingRaw(self.patch(url, json=data).json())

    def create_finding(self, data: dict) -> FindingRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        return FindingRaw(self.post(url, json=data).json())

    def create_finding_from_template(self, template_id: str, language: typing.Optional[str] = None) -> FindingRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/fromtemplate/")
        data = {"template": template_id}
        if language:
            data["template_language"] = language
        return FindingRaw(self.post(url, json=data).json())

    def _update_section(self, section_id: str, data: dict) -> SectionRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/sections/{section_id}/")
        return SectionRaw(self.patch(url, json=data).json())

    def update_report_fields(self, data: dict) -> typing.List[SectionRaw]:
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
                sections.append(self._update_section(section_id, section_data))
        return sections

    def update_project(self, data: dict) -> Project:
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        return Project(
            self.patch(url, json=data).json(),
            self.reptor.api.project_designs.project_design,
        )

    def update_project_design(self, design_id, force=False) -> Project:
        data = {
            "project_type": design_id,
            "force_change_project_type": True if force else False,
        }
        try:
            return self.update_project(data)
        except HTTPError as e:
            raise (HTTPError(e.response.text))

    def get_enabled_language_codes(
        self,
    ) -> list:  # TODO should not be in ProjectsAPI probably
        url = urljoin(self.reptor.get_config().get_server(), "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            language["code"] for language in settings.get("languages", list()) if language["enabled"] is True
        ]
        return languages
