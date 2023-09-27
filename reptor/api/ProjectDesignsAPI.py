from functools import cached_property
from posixpath import join as urljoin
import typing

from reptor.api.APIClient import APIClient
from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignOverview


class ProjectDesignsAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = (
            f"{self.reptor.get_config().get_server()}/api/v1/projecttypes/"
        )

        self.project_design_id = kwargs.get("project_design_id", "")
        self.object_endpoint = urljoin(self.base_endpoint, self.project_design_id)

    def get_project_designs(
        self, scope: typing.Optional[str] = "global"
    ) -> typing.List[ProjectDesignOverview]:
        url = self.base_endpoint
        params = {}
        if scope:
            params["scope"] = scope
        response = self.get(url, params=params)
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(ProjectDesignOverview(item))
        return return_data

    @cached_property
    def project_design(self) -> ProjectDesign:
        """Gets project design

        Args:
            readonly (bool, optional): Only archived projects. Defaults to False.

        Returns:
            ProjectDesign object
        """
        if not self.project_design_id:
            raise ValueError("Missing Project Design ID")

        response = self.get(self.object_endpoint)
        return ProjectDesign(response.json())
