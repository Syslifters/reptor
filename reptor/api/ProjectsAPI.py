import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.api.models import Project, Finding


class ProjectsAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = (
            f"{self.reptor.get_config().get_server()}/api/v1/pentestprojects/"
        )

        self.object_endpoint = f"{self.base_endpoint}/{self.project_id}"

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
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        response = self.get(url)
        return Project(response.json())

    def export(self, file_name: typing.Optional[pathlib.Path] = None):
        """Exports a Project to a .tar.gz file locally.

        Args:
            file_name (typing.Optional[pathlib.Path], optional): Local File path. Defaults to None.

        Raises:
            ValueError: Requires project_id
        """
        if not self.project_id:
            raise ValueError("No project ID. Wanna run 'reptor conf'?")

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

    def get_findings(self) -> typing.List[Finding]:
        """Gets all findings of a project

        Returns:
            typing.List[Finding]: List of findings for this project
        """
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url)

        return_data = list()
        for item in response.json():
            return_data.append(Finding(item))
        return return_data

    def update_finding(self, finding_id: str, data: dict) -> None:
        # Todo: Should accept a finding object ?
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        self.patch(url, data)

    def update_project(self, data: dict) -> None:
        # Todo: Should return an updated object?
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        self.patch(url, data)

    def get_enabled_language_codes(self) -> list:
        url = urljoin(self.reptor.get_config().get_server(), "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            l["code"] for l in settings.get("languages", list()) if l["enabled"] == True
        ]
        return languages
