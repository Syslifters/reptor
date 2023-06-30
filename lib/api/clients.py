
import typing

from datetime import datetime
from posixpath import join as urljoin

import requests

import utils.conf

class APIClient:
    """Base API Client, holds all endpoint configuration and supplies subclasses with HTTP methods

    """
    server : str = None # From config file the server we talk to
    project_id : str = None # From config, if a project is set
    token : str = None # Auth Token for the API...
    endpoint : str = None # Endpoints are defined in the sub classes, depending on Project ID & Item ID
    item_id : str = None # Can be a Note ID, Project ID, Finding ID, User ID etc

    def __init__(self) -> None:
        if "server" in utils.conf.config:
            self.server = utils.conf.config['server']

        if "project_id" in utils.conf.config:
            self.project_id = utils.conf.config['project_id']

        if "token" in utils.conf.config:
            self.token = utils.conf.config['token']

    def _get_headers(self) -> typing.Dict:
        return {'Referer': self.endpoint,
                'Content-Type': 'application/json',
                "User-Agent": "reptor CLI v:0.0.1?" # Todo: Might want to consider a user-agent
                }

    def _get_full_endpoint_url(self) -> str:
        return urljoin(self.server, self.endpoint)

    def get_endpoint_by_id(self, item_id : str) -> str:
        return urljoin(self.server, self.endpoint, item_id)

    def get(self, url = None):
        """Sends a get request
        """
        if not url:
            url = self._get_full_endpoint_url()

        self.response = requests.get(
            url,
            headers=self._get_headers(),
            cookies={'sessionid': self.token},
            verify=False # Todo: Should be a CLI param for people with self-hosted version
        )
        self.response.raise_for_status()

    def get_by_id(self, item_id):
        """Get a single item by ID

        Args:
            item_id (str): Any ID of Parent Class Item
        """
        url = self._get_full_endpoint_url()
        url = urljoin(url, item_id)
        self.get(url)
        return self.response.json()


    def get_list(self):
        """Gets list of items
        """
        url = self._get_full_endpoint_url()
        self.get(url)
        return self.response.json()


    def post(self, data, url = None):
        """Sends a post requests, requires some json data

        Args:
            data (_type_): _description_
        """
        if not url:
            url = self._get_full_endpoint_url()

        self.response = requests.post(
            url,
            headers=self._get_headers(),
            cookies={'sessionid': self.token},
            json=data,
            verify=False # Todo: Should be a CLI param for people with self-hosted version
        )
        self.response.raise_for_status()

    def put(self, data, url = None):
        """Sends a put requests, requires some json data

        Args:
            data (_type_): _description_
        """
        if not url:
            url = self._get_full_endpoint_url()

        self.response = requests.put(
            url,
            headers=self._get_headers(),
            cookies={'sessionid': self.token},
            json=data,
            verify=False # Todo: Should be a CLI param for people with self-hosted version
        )
        self.response.raise_for_status()


class NotesApi(APIClient):
    """Interacts with Notes Endpoints

    Args:
        APIClient (_type_): _description_
    """
    def __init__(self) -> None:
        super().__init__()

        if self.project_id:
            self.endpoint = f"api/v1/pentestprojects/{self.project_id}/notes"
        else:
            self.endpoint = f"api/v1/pentestusers/self/notes/"

        if self.item_id:
            self.endpoint = f"api/v1/pentestusers/self/notes/{self.item_id}"

    def create(self, data) -> any:
        # Todo: Error handling
        self.post(data)
        return self.response.json()

    def set_icon(self, notes_id : str, icon : str ):
        if not notes_id:
            # Todo: Throw error ?
            return

        self.item_id = notes_id

        self.put({
            "icon_emoji": icon
        })

    def write(self, data):
        # Todo: Implement
        ...

class ProjectsApi(APIClient):

    endpoint = f"api/v1/pentestprojects/"

    def __init__(self) -> None:
        super().__init__()

        if self.project_id:
            self.endpoint = f"api/v1/pentestprojects/{self.project_id}"

        if self.item_id:
            self.endpoint = f"api/v1/pentestprojects/{self.item_id}"

class FindingsApi(APIClient):

    endpoint = f"api/v1/findingtemplates/"

    def __init__(self) -> None:
        super().__init__()