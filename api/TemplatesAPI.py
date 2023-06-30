from api.APIClient import APIClient
from posixpath import join as urljoin


class TemplatesAPI(APIClient):

    def __init__(self) -> None:
        super().__init__()

        self.base_endpoint = urljoin(self.server, f"api/v1/findingtemplates/")
        self.object_endpoint = urljoin(
            f"api/v1/findingtemplates/{self.project_id}")


    def get_templates(self):
        """Gets list of Templates
        """
        response = self.get(self.base_endpoint)
        return response.json()['results']

    def search(self, search_term):
        """Searches through the templates
        """

        response = self.get(urljoin(self.base_endpoint, f"?search={search_term}") )
        return response.json()['results']