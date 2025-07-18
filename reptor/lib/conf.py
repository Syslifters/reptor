import os
import typing
from posixpath import join as urljoin
from uuid import UUID

import yaml

from .. import settings as settings


class Config:
    _raw_config: dict = {
        "server": "https://demo.sysre.pt",
        "token": None,
        "project_id": None,
        "log_file": False,
    }
    _no_config_file: bool = False

    """These keys are ignored when writing the config to a file
    By default this should be cli and insecure
    """
    _ignored_keys_in_config = ["cli", "insecure"]

    def __new__(cls):
        """Make the Config Singleton

        This helps to ensure, that there cannot be two different
        configurations while running the program.

        Returns:
            Config: current Config Object
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def get(
        self, key: str, default: typing.Optional[typing.Any] = None, plugin: str = ""
    ) -> typing.Any:
        """Returns a value from the current config

        Args:
            key (_type_): _description_
            default (typing.Any, optional): _description_. Defaults to None.

        Returns:
            typing.Any: _description_
        """
        if plugin:
            return (self._raw_config.get(plugin) or dict()).get(key, default)
        else:
            return self._raw_config.get(key, default)

    def items(self, plugin: str = "") -> typing.ItemsView[str, typing.Any]:
        if plugin:
            return (self._raw_config.get(plugin) or dict()).items()
        else:
            return self._raw_config.items()

    def set(self, key: str, value: typing.Any, plugin: str = ""):
        """Sets a value in the config

        Args:
            key (typing.Any): _description_
            value (typing.Any): _description_
        """
        if plugin:
            plugin_settings = self._raw_config.get(plugin, {})
            plugin_settings.update({key: value})
            self._raw_config.update({plugin: plugin_settings})
        else:
            self._raw_config.update({key: value})

    def load_config(
        self,
        server: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
        project_id: typing.Optional[str] = None,
        personal_note: bool = False,
        return_only: bool = False,
    ) -> dict:
        """Loads config file from user home directory"""
        config = dict()
        try:
            with open(settings.PERSONAL_CONFIG_FILE, "r") as f:
                config = yaml.safe_load(f.read())
            if not config:
                config = {}
                self._no_config_file = True
        except FileNotFoundError:
            self._no_config_file = True
        config["server"] = os.environ.get("REPTOR_SERVER", config.get("server"))
        config["token"] = os.environ.get("REPTOR_TOKEN", config.get("token"))
        config["project_id"] = os.environ.get("REPTOR_PROJECT_ID", config.get("project_id"))
        config["personal_note"] = personal_note
        if server:
            config["server"] = server
        if token:
            config["token"] = token
        if project_id:
            config["project_id"] = project_id

        if requests_ca_bundle := os.environ.get("REQUESTS_CA_BUNDLE", config.get("requests_ca_bundle")):
            os.environ["REQUESTS_CA_BUNDLE"] = requests_ca_bundle

        for k, v in self.get_cli_overwrite().items():
            if v:
                config[k] = v

        if not return_only:
            self._raw_config = config
        return config

    def get_config_from_user(self):
        """Asks the user for the individiual settings and offers to
        write them into a config file
        """
        default_server = self._raw_config.get("server") or ""
        self._raw_config["server"] = (
            input(f"Server [{default_server}]: ") or default_server
        )

        default_api_token = (
            self._raw_config.get("token")
            or f'Create at {urljoin(self._raw_config["server"], "users/self/apitokens/")}'
            if self._raw_config["server"].startswith("http")
            else ""
        )
        self._raw_config["token"] = input(
            f"API Token{ ' [redacted]' if default_api_token else ''}: "
        ) or self._raw_config.get("token")
        if self._raw_config["token"]:
            self._raw_config["token"] = (
                self._raw_config["token"]
                .replace("Authorization: ", "")
                .replace("Bearer ", "")
                .strip()
            )

        default_project_id = self._raw_config.get("project_id")
        self._raw_config["project_id"] = (
            input(
                f"Project ID (optional){ f' [{default_project_id}]' if default_project_id else ''}: "
            )
            or default_project_id
        )

        self.store_config()

    def store_config(self):
        """Offer user to write temporary config to local config file"""
        store = None
        while store not in ["y", "n"]:
            store = input(
                f"Store to config to {settings.PERSONAL_CONFIG_FILE}? [y/n]: "
            )[:1].lower()
        if store == "y":
            self._write_to_file()
        self.instance._raw_config = self._raw_config

    def _write_to_file(self, config: typing.Optional[dict] = None):
        """Writes config file as yaml file"""
        if not config:
            config = self._raw_config
        if config:
            settings.PERSONAL_SYSREPTOR_HOME.mkdir(exist_ok=True)                
            try:
                with open(settings.PERSONAL_CONFIG_FILE, "r") as f:
                    new_config = yaml.safe_load(f.read()) or {}
            except (FileNotFoundError, yaml.YAMLError):
                new_config = {}
            new_config.update({
                k: v
                for k, v in config.items()
                if k not in self._ignored_keys_in_config
            })
            with open(settings.PERSONAL_CONFIG_FILE, "w") as f:
                yaml.dump(new_config, f, encoding="utf-8")
        else:
            raise ValueError("No config is currently set")

    def get_server(self) -> str:
        """Always returns the server url without the final /

        When you concat the server url you are responsible for starting with /

        i.e:

            f"{self.reptor.get_config().get_server()}/api/v1/pentestprojects"

        Returns:
            str: _description_
        """
        server_url = self.get("server", "")
        if not server_url:
            raise ValueError(
                "No SysReptor server. Try 'reptor conf' or use '--server'."
            )
        if server_url[-1:] == "/":
            server_url = server_url[:-1]
        return server_url

    def get_token(self) -> str:
        """The Token is required to connect to the Rest API

        Returns:
            str: Token to Authenticate
        """
        if token := self.get("token"):
            return token
        else:
            raise ValueError(
                "No SysReptor API token. Try 'reptor conf' or use '--token'."
            )

    def get_project_id(self) -> str:
        """Do not use this, instead use self.reptor.get_active_project_id()
        This will query the Project ID from the actual config.
        Can be overwritten via CLI
        Returns:
            str: Project ID
        """
        if project_id := self.get("project_id"):
            try:
                UUID(project_id)
                return project_id
            except ValueError:
                raise ValueError(f"Project ID ('{project_id}') is not a valid UUID.")
        return ""

    def get_cli_overwrite(self) -> typing.Dict:
        """Gives access to the entire CLI arguments.
        If not found, it will return an empty dict

        Returns:
            typing.Dict: Holds all CLI arguments
        """
        return self.get("cli", {})

    def get_log_file(self) -> bool:
        """Checks if the user wants to keep a log file in their home directory

        Returns:
            bool: True to keep logs in a file
        """
        return self.get("log_file", False)
