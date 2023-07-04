import typing
from posixpath import join as urljoin

from api.APIClient import APIClient
from api.models import FindingTemplate


class TemplatesAPI(APIClient):
    def __init__(self, reptor) -> None:
        super().__init__(reptor)

        self.base_endpoint = urljoin(self._get_server(), f"api/v1/findingtemplates/")
        self.object_endpoint = urljoin(
            f"api/v1/findingtemplates/{self._get_project_id()}"
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
