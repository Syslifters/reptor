import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.models.Finding import Finding, FindingRaw
from reptor.models.Section import Section, SectionRaw
from reptor.models.Project import Project


class ProjectsAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
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

    def get_projects(self, readonly: bool = False) -> typing.List[Project]:
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
            return_data.append(Project(item))
        return return_data

    def search(self, search_term: Optional[str] = "") -> typing.List[Project]:
        """Searches projects by search term and retrieves all projects that match

        Args:
            search_term (Optional[str], optional): Search Term to look for. Defaults to None.

        Returns:
            typing.List[Project]: List of projects that match search
        """

        response = self.get(f"{self.base_endpoint}?search={search_term}")

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(Project(item))
        return return_data

    def get_project(self) -> Project:
        if not self.project_id:
            raise ValueError("Make sure you have a project specified.")
        url = self.object_endpoint
        response = self.get(url)
        # TODO we might want to save Project to attribute to avoid redundant requests
        return Project(response.json())

    def export(self, file_name: typing.Optional[pathlib.Path] = None):
        """Exports a Project to a .tar.gz file locally.

        Args:
            file_name (typing.Optional[pathlib.Path], optional): Local File path. Defaults to None.

        Raises:
            ValueError: Requires project_id
        """
        if not self.project_id:
            raise ValueError(
                "No project ID. Specify in reptor conf or via -p / --project-id"
            )

        if not file_name:
            filepath = pathlib.Path().cwd()
            file_name = filepath / f"{self.project_id}.tar.gz"

        url = urljoin(self.base_endpoint, f"{self.project_id}/export/all")
        data = self.post(url)
        with open(file_name, "wb") as f:
            f.write(data.content)

    def duplicate(self) -> Project:
        """Duplicates Projects

        Returns:
            Project: Project Object
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/copy/")
        duplicated_project = self.post(url).json()
        return Project(duplicated_project)

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
            section = Section(self.project_design, SectionRaw(item))
            return_data.append(section)
        return return_data

    def get_findings(self) -> typing.List[Finding]:
        """Gets all findings of a project

        Returns:
            typing.List[Finding]: List of findings for this project
        """
        return_data = list()
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url).json()

        if not response:
            return return_data

        if not self.project_design:
            self.project_design = self.reptor.api.project_designs.project_design

        for item in response:
            finding = Finding(FindingRaw(item), project_design=self.project_design)
            return_data.append(finding)
        return return_data

    def update_finding(self, finding_id: str, data: dict) -> dict:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        return self.patch(url, data).json()

    def update_section(self, section_id: str, data: dict) -> dict:
        url = urljoin(self.base_endpoint, f"{self.project_id}/sections/{section_id}/")
        return self.patch(url, data).json()

    def update_project(self, data: dict) -> dict:
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        return self.patch(url, data).json()

    def get_enabled_language_codes(self) -> list:
        url = urljoin(self.reptor.get_config().get_server(), "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            l["code"] for l in settings.get("languages", list()) if l["enabled"] == True
        ]
        return languages
