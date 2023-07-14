import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.api.models import Project, FindingData


class ProjectsAPI(APIClient):
    project_id: str  # This is a local overwrite to quickly check other projects

    def __init__(self, reptor, project_id: str = None) -> None:
        super().__init__(reptor)

        self.base_endpoint = urljoin(
            self._config.get_server(), f"api/v1/pentestprojects/"
        )
        self.object_endpoint = urljoin(
            self.base_endpoint, f"{self._config.get_project_id()}"
        )
        if project_id:
            self.project_id = project_id
        else:
            self.project_id = self._config.get_project_id()

        if not self.project_id:
            raise ValueError("No project ID. Wanna run 'reptor conf'?")

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

    def export(self, file_name: pathlib.Path = None) -> bytes:
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

    def get_findings(self) -> typing.List(FindingData):
        url = urljoin(self.base_endpoint, f"{self.project_id}/findings/")
        response = self.get(url)

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(FindingData(item))
        return return_data
