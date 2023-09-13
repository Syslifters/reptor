import typing
from contextlib import contextmanager
from functools import cached_property
from posixpath import join as urljoin
from typing import Optional

from requests import HTTPError

from reptor.api.APIClient import APIClient
from reptor.models.Finding import FindingRaw
from reptor.models.Project import Project, ProjectOverview
from reptor.models.Section import Section, SectionRaw


class ProjectsAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._init_attrs()

    def _init_attrs(self) -> None:
        self.project_design = None

        if not (server := self.reptor.get_config().get_server()):
            raise ValueError("No SysReptor server configured. Try 'reptor conf'.")
        if not self.project_id:
            raise ValueError(
                "No Project ID configured. Try 'reptor conf' or use '--project-id'."
            )

        self.base_endpoint = f"{server}/api/v1/pentestprojects"

        self.object_endpoint = urljoin(self.base_endpoint, self.project_id)
        self.debug(self.base_endpoint)

    def get_projects(self, readonly: bool = False) -> typing.List[ProjectOverview]:
        """Gets list of projects

        Args:
            readonly (bool, optional): Only archived projects. Defaults to False.

        Returns:
            json: List of all Projects
        """
        url = self.base_endpoint
        if readonly:
            url = f"{url}?readonly=true"
        response = self.get(url)
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(ProjectOverview(item))
        return return_data

    def search(self, search_term: Optional[str] = "") -> typing.List[ProjectOverview]:
        """Searches projects by search term and retrieves all projects that match

        Args:
            search_term (Optional[str], optional): Search Term to look for. Defaults to None.

        Returns:
            typing.List[Project]: List of project overviews (without sections, findings) that match search
        """

        response = self.get(f"{self.base_endpoint}?search={search_term}")

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(ProjectOverview(item))
        return return_data

    @cached_property
    def project(self) -> Project:
        return self._get_project()

    def _get_project(self) -> Project:
        url = self.object_endpoint
        response = self.get(url)
        return Project(response.json())

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

    def delete_project(self) -> None:
        url = self.object_endpoint
        self.delete(url)

    def duplicate(self) -> Project:
        """Duplicates Projects

        Returns:
            Project: Project Object
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/copy/")
        duplicated_project = self.post(url).json()
        return Project(duplicated_project)

    @contextmanager
    def duplicate_and_cleanup(self):
        original_project_id = self.project_id
        duplicated_project = self.duplicate()
        self.switch_project(duplicated_project.id)
        self.log.info(f"Duplicated project to {duplicated_project.id}")

        yield

        self.delete_project()
        self.switch_project(original_project_id)
        self.log.info(f"Cleaned up duplicated project")

    def switch_project(self, new_project_id) -> None:
        self.reptor._config._raw_config["project_id"] = new_project_id
        self.project_id = new_project_id
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

    def update_finding(self, finding_id: str, data: dict) -> FindingRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        return FindingRaw(self.patch(url, data).json())

    def create_finding(self, data: dict) -> FindingRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        return FindingRaw(self.post(url, data).json())

    def create_finding_from_template(self, template_id: str) -> FindingRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/fromtemplate/")
        return FindingRaw(self.post(url, {"template": template_id}).json())

    def update_section(self, section_id: str, data: dict) -> SectionRaw:
        url = urljoin(self.base_endpoint, f"{self.project_id}/sections/{section_id}/")
        return SectionRaw(self.patch(url, data).json())

    def update_project(self, data: dict) -> Project:
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        return Project(self.patch(url, data).json())

    def update_project_design(self, design_id, force=False) -> Project:
        data = {
            "project_type": design_id,
            "force_change_project_type": True if force else False,
        }
        try:
            return self.update_project(data)
        except HTTPError as e:
            raise(HTTPError(e.response.text))

    def get_enabled_language_codes(
        self,
    ) -> list:  # TODO should not be in ProjectsAPI probably
        url = urljoin(self.reptor.get_config().get_server(), "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            l["code"] for l in settings.get("languages", list()) if l["enabled"] == True
        ]
        return languages
