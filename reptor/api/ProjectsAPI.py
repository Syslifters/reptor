import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.api.models import Project, Finding


class ProjectsAPI(APIClient):
    project_id: str  # This is a local overwrite to quickly check other projects

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = (
            f"{self.reptor.get_config().get_server()}/api/v1/pentestprojects/"
        )
        if kwargs.get("project_id", ""):
            self.project_id = kwargs.get("project_id", "")
        else:
            self.project_id = self.reptor.get_config().get_project_id()

        # if not self.project_id:
        #     self.reptor.logger.fail_with_exit("No project ID. Wanna run 'reptor conf'?")
        self.object_endpoint = pathlib.Path(self.base_endpoint) / f"{self.project_id}/"

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

    def search(self, search_term: Optional[str] = None) -> typing.List[Project]:
        """Searches for search term"""
        if not search_term:
            raise ValueError("search_term is missing")

        response = self.get(f"{self.base_endpoint}?search={search_term}")

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(Project(item))
        return return_data

    def get_project(self) -> Project:
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        response = self.get(url)
        return Project(response.json())

    def export(
        self, file_name: typing.Optional[pathlib.Path] = None
    ) -> typing.Optional[bytes]:
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
        url = urljoin(self.base_endpoint, f"{self.project_id}/copy/")
        duplicated_project = self.post(url).json()
        return Project(duplicated_project)

    def get_findings(self) -> typing.List[Finding]:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url)

        return_data = list()
        for item in response.json():
            return_data.append(Finding(item))
        return return_data

    def update_finding(self, finding_id: str, data: dict) -> None:
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/{finding_id}/")
        self.patch(url, data)

    def update_project(self, data: dict) -> None:
        url = urljoin(self.base_endpoint, f"{self.project_id}/")
        self.patch(url, data)

    def get_enabled_language_codes(self) -> list:
        url = urljoin(self.reptor.get_config().get_server(), "api/v1/utils/settings/")
        settings = self.get(url).json()
        languages = [
            l["code"] for l in settings.get("languages", list()) if l["enabled"] == True
        ]
        return languages
