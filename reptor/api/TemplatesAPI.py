import typing
from posixpath import join as urljoin

from reptor.api.APIClient import APIClient
from reptor.models.FindingTemplate import FindingTemplate


class TemplatesAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = urljoin(
            self.reptor.get_config().get_server(), f"api/v1/findingtemplates/"
        )
        self.object_endpoint = urljoin(f"api/v1/findingtemplates/{self.project_id}")

    def get_template_overview(self) -> typing.List[FindingTemplate]:
        """Gets list of Templates"""
        response = self.get(self.base_endpoint)
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(FindingTemplate(item))
        return return_data

    def get_template(self, template_id: str) -> FindingTemplate:
        """Gets a single Template by ID"""
        response = self.get(urljoin(self.base_endpoint, template_id))
        return FindingTemplate(response.json())

    def export(self, template_id: str) -> bytes:
        """Exports a template in archive format (tar.gz)"""
        url = urljoin(self.base_endpoint, f"{template_id}/export/")
        return self.post(url).content

    def search(
        self, search_term, deduplicate: bool = True
    ) -> typing.List[FindingTemplate]:
        """Searches through the templates"""

        response = self.get(urljoin(self.base_endpoint, f"?search={search_term}"))
        return_data = list()
        added_ids = set()
        for item in response.json()["results"]:
            finding_template = FindingTemplate(item)
            if finding_template.id not in added_ids:
                return_data.append(FindingTemplate(item))
            if deduplicate:
                added_ids.add(finding_template.id)
        return return_data

    def upload_new_template(
        self, template: FindingTemplate
    ) -> typing.Optional[FindingTemplate]:
        """Uploads a new Finding Template to API

        Args:
            template (FindingTemplate): Model Data to upload

        Returns:
            FindingTemplate: Updated Model with ID etc.
        """
        res = self.post(
            self.base_endpoint,
            json=template.to_dict(),
        )
        return FindingTemplate(res.json())
