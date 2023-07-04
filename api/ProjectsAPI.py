import typing
import pathlib
from posixpath import join as urljoin

from api.APIClient import APIClient
from api.models import Project


class ProjectsAPI(APIClient):
    project_id: str  # This is a local overwrite to quickly check other projects

    def __init__(self, reptor) -> None:
        super().__init__(reptor)

        self.base_endpoint = urljoin(
            self._config.get_server(), f"api/v1/pentestprojects/"
        )
        self.object_endpoint = urljoin(
            self.base_endpoint, f"{self._config.get_project_id()}"
        )

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

    def search(self, search_term: str | None = None) -> typing.List[Project]:
        """Searches for search term"""
        if not search_term:
            raise ValueError("search_term is missing")

        response = self.get(f"{self.base_endpoint}?search={search_term}")

        return_data = list()
        for item in response.json()["results"]:
            return_data.append(Project(item))
        return return_data

    def export(self, project_id: str | None = None):
        if project_id:
            self.project_id = project_id

        if not project_id:
            raise ValueError

        filepath = pathlib.Path().cwd()
        file_name = filepath / f"{project_id}.tar.gz"
        print(f"Writing to: {file_name}")

        url = urljoin(self.base_endpoint, f"{self.project_id}/export/all")
        data = self.post(url)
        with open(file_name, "wb") as f:
            f.write(data.content)
