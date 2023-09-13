import typing

import requests

import reptor.settings as settings
from reptor.lib.console import reptor_console


class APIClient:
    """Base API Client, holds all endpoint configuration and supplies subclasses with HTTP methods"""

    reptor: typing.Any
    base_endpoint: str
    endpoint: str
    item_id: str
    force_unlock: bool
    project_id: str

    def __init__(self, require_project_id=True, **kwargs) -> None:
        self.reptor = kwargs.get("reptor", None)
        if not self.reptor:
            reptor_console.print(
                "[red]Make sure you access the API via the apimanager (reptor.api)[/red]"
            )
            exit(1)
        self.verify = not self.reptor.get_config().get("insecure", False)

        try:
            self.project_id = self.reptor.get_active_project_id()
            self.debug(f"Project ID is {self.project_id}")
        except ValueError as e:
            if require_project_id:
                raise e
            self.project_id = ""

    def _get_headers(self, json_content=False) -> typing.Dict:
        headers = dict()
        if json_content:
            headers["Content-Type"] = "application/json"
        headers["User-Agent"] = settings.USER_AGENT
        headers["Authorization"] = f"Bearer {self.reptor.get_config().get_token()}"
        self.debug(f"HTTP Headers: {headers}")
        return headers

    @property
    def log(self):
        """Access the logging directly from plugin

        Returns:
            ReptorAdapter: Logging Module
        """
        return self.reptor.get_logger()

    @property
    def console(self):
        """Access the rich console that allows markdown etc.

        Returns:
            Console: rich console
        """
        return reptor_console

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def success(self, msg, *args, **kwargs):
        """Use this to print Green text by default. You can change colors etc.

        See the logger.py for examples.

        Args:
            msg (str): Any message you want to print
        """
        self.log.success(msg, *args, **kwargs)

    def display(self, msg, *args, **kwargs):
        """Use this to print blue text by default. You can change colors etc.

        See the logger.py for examples.

        Args:
            msg (str): Any message you want to print
        """
        self.log.display(msg, *args, **kwargs)

    def highlight(self, msg, *args, **kwargs):
        """Prints a yellow message. Good for highlighting certain
        output.

        Args:
            msg (str): Any message you want to print
        """
        self.log.highlight(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Default DEBUG method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in DEBUG log
        """
        self.log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Default INFO method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in INFO log
        """
        self.log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Default WARNING method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in WARNING log
        """
        self.log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Default ERROR method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in ERROR log
        """
        self.log.error(msg, *args, **kwargs)

    def get(self, url: str) -> requests.models.Response:
        """Sends a get request

        Args:
            url (str): Endpoint URL

        Returns:
            requests.models.Response: Returns requests Response Object
        """
        self.debug(f"GET URL:{url}")
        response = requests.get(
            url,
            headers=self._get_headers(),
            verify=self.verify,
        )
        self.debug(f"Received response: {response.content}")
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

        self.reptor.logger.debug(f"POST URL: {url}")

        response = requests.post(
            url,
            headers=self._get_headers(json_content=json_content),
            json=data,
            files=files,
            verify=self.verify,
        )
        self.debug(f"Received response: {response.content}")
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
        self.debug(f"PUT URL:{url}")
        response = requests.put(
            url,
            headers=self._get_headers(),
            json=data,
            verify=self.verify,
        )
        self.debug(f"Received response: {response.content}")
        response.raise_for_status()
        return response

    def patch(self, url: str, data: object) -> requests.models.Response:
        """Sends a patch requests, requires some json data

        Args:
            url (str): Endpoint URL
            data (object): JSON Data

        Returns:
            requests.models.Response: requests Respone Object
        """
        self.debug(f"PATCH URL:{url}")
        response = requests.patch(
            url,
            headers=self._get_headers(),
            json=data,
            verify=self.verify,
        )
        self.debug(f"Received response: {response.content}")
        response.raise_for_status()
        return response

    def delete(self, url: str) -> requests.models.Response:
        """Sends a delete request

        Args:
            url (str): Endpoint URL

        Returns:
            requests.models.Response: Returns requests Response Object
        """
        self.debug(f"DELETE URL:{url}")
        response = requests.delete(
            url,
            headers=self._get_headers(),
            verify=self.verify,
        )
        self.debug(f"Received response: {response.content}")
        response.raise_for_status()
        return response
