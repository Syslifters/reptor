import pathlib
import typing
from posixpath import join as urljoin
from typing import Optional

from reptor.api.APIClient import APIClient
from reptor.api.models import ProjectDesign


class ProjectDesignsAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = (
            f"{self.reptor.get_config().get_server()}/api/v1/projecttypes/"
        )

        self.project_design_id = kwargs.get("project_design_id", "")
        self.object_endpoint = f"{self.base_endpoint}/{self.project_design_id}/"

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
