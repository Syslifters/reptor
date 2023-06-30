from api.APIClient import APIClient
from posixpath import join as urljoin


class ProjectsAPI(APIClient):
    def __init__(self) -> None:
        super().__init__()

        self.base_endpoint = urljoin(self.server, f"api/v1/pentestprojects/")
        self.object_endpoint = urljoin(
            f"api/v1/pentestprojects/{self.project_id}")

    def get_projects(self):
        """Gets list of projects
        """
        self.get(self.base_endpoint)
        return self.response.json()['results']
