from functools import cached_property
from posixpath import join as urljoin
import typing

from reptor.models.Finding import FindingDataRaw
from reptor.models.Section import SectionDataRaw
from reptor.api.APIClient import APIClient
from reptor.models.ProjectDesign import (
    ProjectDesign,
    ProjectDesignField,
    ProjectDesignOverview,
    merge_report_fields_into_sections,
)


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
    
    def create_project_design(self, name: str, scope: typing.Optional[str] = "global") -> ProjectDesign:
        """Creates a new project design with the given name.

        Args:
            name (str): Name of the project design to create.
            scope (str, optional): Scope of the project design ("global" or "private"). Defaults to "global".

        Returns:
            The created ProjectDesign object.
        """
        payload = {"name": name, "scope": scope}
        response = self.post(self.base_endpoint, json=payload)
        return ProjectDesign(response.json())
    
    def update_project_design(
            self,
            project_design_id: str,
            report_template: typing.Optional[str] = None,
            report_styles: typing.Optional[str] = None,
            preview_findings: typing.Optional[typing.List[FindingDataRaw]] = None,
            preview_report: typing.Optional[SectionDataRaw] = None,
            finding_fields: typing.Optional[typing.List[ProjectDesignField]] = None,
            report_fields: typing.Optional[typing.List[ProjectDesignField]] = None,
            report_sections: typing.Optional[typing.List[dict]] = None,
        ) -> ProjectDesign:
        """Updates the project design with the given id.

            Args:
                project_design_id (str): ID of the project design to update.
                report_template (str, optional): Report design HTML source. None value means no update. Defaults to None.
                report_styles (str, optional): Report CSS styles to update. None value means no update. Defaults to None.
                preview_findings (List[FindingDataRaw], optional): Preview findings to update. Defaults to None.
                preview_report (SectionDataRaw, optional): Preview report sections to update. Defaults to None.
                finding_fields (List[ProjectDesignField], optional): Finding field definitions to update. Defaults to None.
                report_fields (List[ProjectDesignField], optional): Report field definitions to update. Merged into
                    ``report_sections`` because the SysReptor API stores report fields inside section definitions.
                    Requires the current design to be fetchable when ``report_sections`` is not provided. Defaults to None.
                report_sections (List[dict], optional): Full report section definitions to update. Defaults to None.
            Returns:
                The updated ProjectDesign object.
        """
        payload = {}
        if report_template is not None:
            payload["report_template"] = report_template
        if report_styles is not None:
            payload["report_styles"] = report_styles
        if preview_findings is not None or preview_report is not None:
            payload["report_preview_data"] = dict()
            if preview_findings is not None:
                payload["report_preview_data"]["findings"] = [finding.to_dict() for finding in preview_findings]
            if preview_report is not None:
                payload["report_preview_data"]["report"] = preview_report.to_dict()
        if finding_fields is not None:
            payload["finding_fields"] = [field.to_api_dict() for field in finding_fields]
        if report_sections is not None:
            payload["report_sections"] = report_sections
        elif report_fields is not None:
            current_design = self.get_project_design(project_design_id=project_design_id)
            payload["report_sections"] = merge_report_fields_into_sections(
                current_design.report_sections,
                report_fields,
            )
        response = self.patch(urljoin(self.base_endpoint, project_design_id), json=payload)
        return ProjectDesign(response.json())

    def delete_project_design(self, project_design_id: str) -> None:
        """Deletes the project design with the given id.

            Args:
                project_design_id (str): ID of the project design to delete.

        Returns:
            None
        """
        self.delete(urljoin(self.base_endpoint, project_design_id))

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

    def get_project_design(self, project_design_id: typing.Optional[str] = None) -> ProjectDesign:
        """Gets the project design in context from SysReptor.

        Args:
            project_design_id (str, optional): ID of the project design to fetch. If not provided, it uses the project design of the project in context.
        
        Returns:
            ProjectDesign object with sections and findings.
        
        Example:
            ```python
            design = reptor.api.project_designs.get_project_design()
            ```
        """
        if project_design_id:
            object_endpoint = urljoin(self.base_endpoint, project_design_id)
        else:
            object_endpoint = self.object_endpoint
        response = self.get(object_endpoint)
        return ProjectDesign(response.json())

    def fetch_project_design(self, project_design_id: typing.Optional[str] = None) -> ProjectDesign:
        """Fetches the project design in context from SysReptor.
        
        .. deprecated::
            Use :meth:`get_project_design` instead. This method will be removed in a future version.

        Args:
            project_design_id (str, optional): ID of the project design to fetch. If not provided, it uses the project design of the project in context.
        
        Returns:
            ProjectDesign object with sections and findings.
        """
        self.log.warning(
            "fetch_project_design() is deprecated and will be removed in a future version. "
            "Use get_project_design() instead."
        )
        return self.get_project_design(project_design_id=project_design_id)

    @cached_property
    def project_design(self) -> ProjectDesign:
        if not self.project_design_id:
            raise ValueError("Missing Project Design ID")

        response = self.get(self.object_endpoint)
        return ProjectDesign(response.json())
