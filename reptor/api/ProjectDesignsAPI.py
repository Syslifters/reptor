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

    def search(
        self, search_term: typing.Optional[str] = "", scope: typing.Optional[str] = "global"
    ) -> typing.List[ProjectDesignOverview]:
        """Searches project designs by search term and scope.

        Args:
            search_term (typing.Optional[str], optional): Search term to look for in project designs. Defaults to "".
            scope (typing.Optional[str], optional): Search scope ("global" or "private"). Defaults to "global".

        Returns:
            List of project design overviews that match the search criteria.
        
        Example:
            ```python
            # Search for all project designs
            designs = reptor.api.project_designs.search()
            
            # Search for specific designs
            webapp_designs = reptor.api.project_designs.search("webapp")
            
            # Search in private scope
            private_designs = reptor.api.project_designs.search(scope="private")
            ```
        """
        
        url = self.base_endpoint
        params = {"search": search_term}
        if scope:
            params["scope"] = scope
        designs_raw = self.get_paginated(url, params=params)
        return [ProjectDesignOverview(item) for item in designs_raw]

    @cached_property
    def project_design(self) -> ProjectDesign:
        """Gets project design of project in context.

        Returns:
            ProjectDesign object for the configured project design ID.
            
        Raises:
            ValueError: If no project design ID is configured.

        Example:
            ```python
            reptor.api.project_designs.project_design
            ```
        """
        if not self.project_design_id:
            raise ValueError("Missing Project Design ID")

        response = self.get(self.object_endpoint)
        return ProjectDesign(response.json())
