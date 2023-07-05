import typing

import requests

import settings

from core.interfaces.conf import ConfigProtocol
from core.interfaces.reptor import ReptorProtocol

from core.logger import reptor_logger


class APIClient:
    """Base API Client, holds all endpoint configuration and supplies subclasses with HTTP methods"""

    _config: ConfigProtocol
    base_endpoint: str
    endpoint: str
    item_id: str
    force_unlock: bool

    def __init__(self, reptor: ReptorProtocol) -> None:
        self._config = reptor.get_config()
        self.verify = not self._config.get("insecure", False)

    def _get_headers(self, json_content=False) -> typing.Dict:
        headers = dict()
        if json_content:
            headers["Content-Type"] = "application/json"
        headers["Referer"] = self.base_endpoint
        headers["User-Agent"] = settings.USER_AGENT
        headers["Authorization"] = f"Bearer {self._config.get_token()}"
        reptor_logger.debug(headers)
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
        return response
