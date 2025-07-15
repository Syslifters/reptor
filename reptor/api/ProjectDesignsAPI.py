from functools import cached_property
from posixpath import join as urljoin
import typing

from reptor.api.APIClient import APIClient
from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignOverview


class ProjectDesignsAPI(APIClient):
    """
    API client for interacting with SysReptor project designs.  

    Note:
        For historic reasons, the SysReptor REST API uses the term "project types" instead of "project designs".  
        "Project types" and "project designs" are the same thing in SysReptor.

    Example:
        ```python
        from reptor import Reptor

        reptor = Reptor(
            server=os.environ.get("REPTOR_SERVER"),
            token=os.environ.get("REPTOR_TOKEN"),
        )

        # ProjectDesignsAPI is available as reptor.api.project_designs, e.g.:
        reptor.api.project_designs.search()
        ```
    """
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

    def fetch_project_design(self, project_design_id: typing.Optional[str] = None) -> ProjectDesign:
        """Fetches the project design in context from SysReptor.

        Args:
            project_design_id (str, optional): ID of the project design to fetch. If not provided, it uses the project design of the project in context.
        
        Returns:
            Project object with sections and findings.
        """
        if project_design_id:
            object_endpoint = urljoin(self.base_endpoint, project_design_id)
        else:
            object_endpoint = self.object_endpoint
        response = self.get(object_endpoint)
        return ProjectDesign(response.json())

    @cached_property
    def project_design(self) -> ProjectDesign:
        if not self.project_design_id:
            raise ValueError("Missing Project Design ID")

        response = self.get(self.object_endpoint)
        return ProjectDesign(response.json())
