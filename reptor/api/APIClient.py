import typing

import requests

import reptor.settings as settings

from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.lib.console import reptor_console


class APIClient:
    """Base API Client, holds all endpoint configuration and supplies subclasses with HTTP methods"""

    reptor: ReptorProtocol
    base_endpoint: str
    endpoint: str
    item_id: str
    force_unlock: bool
    project_id: str

    def __init__(self, **kwargs) -> None:
        self.reptor = kwargs.get("reptor", None)
        if not self.reptor:
            reptor_console.print(
                "[red]Make sure you access the API via the apimanager (reptor.api)[/red]"
            )
            exit(1)
        self.verify = not self.reptor.get_config().get("insecure", False)
        self.project_id = kwargs.get("project_id", "")

    def _get_headers(self, json_content=False) -> typing.Dict:
        headers = dict()
        if json_content:
            headers["Content-Type"] = "application/json"
        headers["User-Agent"] = settings.USER_AGENT
        headers["Authorization"] = f"Bearer {self.reptor.get_config().get_token()}"
        self.reptor.logger.debug(f"HTTP Headers: {headers}")
        return headers

    def get(self, url: str) -> requests.models.Response:
        """Sends a get request

        Args:
            url (str): Endpoint URL

        Returns:
            requests.models.Response: Returns requests Response Object
        """
        response = requests.get(
            url,
            headers=self._get_headers(),
            verify=self.verify,
        )
        response.raise_for_status()
        self.reptor.get_logger().debug(f"Received response: {response.content}")
        return response

    def post(
        self, url: str, data=None, files=None, json_content: bool = True
    ) -> requests.models.Response:
        """Sends a post requests, requires some json data

        Args:
            url (str): Endpoint URL
            data (_type_, optional): _description_. Defaults to None.
            files (_type_, optional): _description_. Defaults to None.
            json_content (bool, optional): _description_. Defaults to True.

        Returns:
            requests.models.Response: Requests Responde Object
        """
        response = requests.post(
            url,
            headers=self._get_headers(json_content=json_content),
            json=data,
            files=files,
            verify=self.verify,
        )
        response.raise_for_status()
        self.reptor.get_logger().debug(f"Received response: {response.content}")
        return response

    def put(self, url: str, data: object) -> requests.models.Response:
        """Sends a put requests, requires some json data

        Args:
            url (str): Endpoint URL
            data (object): JSON Data

        Returns:
            requests.models.Response: requests Respone Object
        """
        response = requests.put(
            url,
            headers=self._get_headers(),
            json=data,
            verify=self.verify,
        )
        response.raise_for_status()
        self.reptor.get_logger().debug(f"Received response: {response.content}")
        return response

    def patch(self, url: str, data: object) -> requests.models.Response:
        """Sends a patch requests, requires some json data

        Args:
            url (str): Endpoint URL
            data (object): JSON Data

        Returns:
            requests.models.Response: requests Respone Object
        """
        response = requests.patch(
            url,
            headers=self._get_headers(),
            json=data,
            verify=self.verify,
        )
        response.raise_for_status()
        self.reptor.get_logger().debug(f"Received response: {response.content}")
        return response
