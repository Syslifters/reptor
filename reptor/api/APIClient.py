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
    _project_id: str

    def __init__(self, require_project_id=True, **kwargs) -> None:
        self.reptor = kwargs.get("reptor", None)
        if not self.reptor:
            reptor_console.print(
                "[red]Make sure you access the API via the apimanager (reptor.api)[/red]"
            )
            exit(1)
        self.verify = not self.reptor.get_config().get("insecure", False)
        if not self.verify:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore

        try:
            self._project_id = self.reptor.get_active_project_id()
            self.debug(f"Project ID is {self._project_id}")
        except ValueError as e:
            if require_project_id:
                raise e
            self._project_id = ""

    @property
    def project_id(self) -> str:
        if not self._project_id:
            raise ValueError(
                "No Project ID configured. Try 'reptor conf' or use '--project-id'."
            )
        return self._project_id

    def _get_headers(self, json_content=True) -> typing.Dict:
        headers = dict()
        if json_content:
            headers["Content-Type"] = "application/json"
        headers["User-Agent"] = settings.USER_AGENT
        headers["Authorization"] = f"Bearer {self.reptor.get_config().get_token()}"
        headers_debug = headers.copy()
        headers_debug["Authorization"] = "[redacted]"
        self.debug(f"HTTP Headers: {headers_debug}")
        return headers

    def _prepare_kwargs(self, kwargs, json_content=True):
        headers = self._get_headers(json_content=json_content)
        if kwargs.get("headers"):
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers
        if not kwargs.get("verify"):
            kwargs["verify"] = self.verify
        return kwargs

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

    def _do_request(
        self, url, method: str = "GET", json_content: bool = True, **kwargs
    ) -> requests.models.Response:
        methods = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "PATCH": requests.patch,
            "DELETE": requests.delete,
        }
        method = method.upper()
        if method not in methods.keys():
            raise ValueError(f"Method {method} not supported")
        self.debug(f"{method} URL: {url}")
        kwargs = self._prepare_kwargs(kwargs, json_content=json_content)
        response = methods[method](url, **kwargs)
        self.debug(f"Received response: {response.content[:1000]}")
        response.raise_for_status()
        return response

    def get(self, *args, **kwargs) -> requests.models.Response:
        return self._do_request(*args, method="GET", **kwargs)

    def post(self, *args, **kwargs) -> requests.models.Response:
        return self._do_request(*args, method="POST", **kwargs)

    def put(self, *args, **kwargs) -> requests.models.Response:
        return self._do_request(*args, method="PUT", **kwargs)

    def patch(self, *args, **kwargs) -> requests.models.Response:
        return self._do_request(*args, method="PATCH", **kwargs)

    def delete(self, *args, **kwargs) -> requests.models.Response:
        return self._do_request(*args, method="DELETE", **kwargs)
