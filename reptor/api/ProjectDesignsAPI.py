import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.api.models import ProjectDesign


class ProjectDesignsAPI(APIClient):
    def __init__(self, reptor, project_design_id: str = None) -> None:
        super().__init__(reptor)

        self.base_endpoint = pathlib.Path(
            self._config.get_server()) / f"api/v1/projecttypes/"

        self.project_design_id = project_design_id
        self.object_endpoint = pathlib.Path(
            self.base_endpoint) / f"{self.project_design_id}/"

    def get_project_design(self) -> ProjectDesign:
        """Gets project design

        Args:
            readonly (bool, optional): Only archived projects. Defaults to False.

        Returns:
            ProjectDesign object
        """
        url = self.object_endpoint
        response = self.get(url)
        return ProjectDesign(response.json())
