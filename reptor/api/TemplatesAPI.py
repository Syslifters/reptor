import typing
from posixpath import join as urljoin

from reptor.api.APIClient import APIClient
from reptor.api.models import FindingTemplate


class TemplatesAPI(APIClient):
    def __init__(self, reptor) -> None:
        super().__init__(reptor)

        self.base_endpoint = urljoin(
            self._config.get_server(), f"api/v1/findingtemplates/"
        )
        self.object_endpoint = urljoin(
            f"api/v1/findingtemplates/{self._config.get_project_id()}"
        )

    def get_templates(self) -> typing.List[FindingTemplate]:
        """Gets list of Templates"""
        response = self.get(self.base_endpoint)
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(FindingTemplate(item))
        return return_data

    def search(self, search_term) -> typing.List[FindingTemplate]:
        """Searches through the templates"""

        response = self.get(urljoin(self.base_endpoint, f"?search={search_term}"))
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(FindingTemplate(item))
        return return_data

    def upload_new_template(self, template: FindingTemplate) -> FindingTemplate | None:
        """Uploads a new Finding Template to API

        Args:
            template (FindingTemplate): Model Data to upload

        Returns:
            FindingTemplate: Updated Model with ID etc.
        """
        res = self.post(self.base_endpoint, data=template._to_api_json())
        raw_data = res.json()
        if raw_data:
            if raw_data["results"]:
                return FindingTemplate(raw_data["results"][0])
        self.reptor.logger.fail(
            f"Could not upload finding with title {template.data.title}"
        )
        return None
