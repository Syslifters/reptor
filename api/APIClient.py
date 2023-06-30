import typing
from posixpath import join as urljoin

import requests

import settings
from utils.conf import config


class APIClient:
    """Base API Client, holds all endpoint configuration and supplies subclasses with HTTP methods

    """
    server: str = None  # From config file the server we talk to
    project_id: str = None  # From config, if a project is set
    token: str = None  # Auth Token for the API...
    endpoint: str = None  # is defined in the sub classes, depending on Project ID & Item ID
    item_id: str = None  # Can be a Note ID, Project ID, Finding ID, User ID etc

    def __init__(self) -> None:
        self.server = config.get('server')
        self.project_id = config.get('project_id')
        self.token = config.get('token')
        self.verify = not config.get('insecure', False)

    def _get_headers(self, json_content=False) -> typing.Dict:
        headers = dict()
        if json_content:
            headers['Content-Type'] = 'application/json'
        headers['Referer'] = self.base_endpoint
        headers['User-Agent'] = settings.USER_AGENT
        return headers

    def get(self, url):
        """Sends a get request
        """
        response = requests.get(
            url,
            headers=self._get_headers(),
            cookies={'sessionid': self.token},
            verify=self.verify,
        )
        response.raise_for_status()
        return response

    def post(self, url, data=None, files=None, json_content=True):
        """Sends a post requests, requires some json data

        Args:
            data (_type_): _description_
        """
        response = requests.post(
            url,
            headers=self._get_headers(json_content=json_content),
            cookies={'sessionid': self.token},
            json=data,
            files=files,
            verify=self.verify,
        )
        response.raise_for_status()
        return response


    def put(self, url, data):
        """Sends a put requests, requires some json data

        Args:
            data (_type_): _description_
        """
        response = requests.put(
            url,
            headers=self._get_headers(),
            cookies={'sessionid': self.token},
            json=data,
            verify=self.verify,
        )
        response.raise_for_status()
        return response
