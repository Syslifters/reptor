import typing

import yaml

from .. import settings as settings

from .interfaces.conf import ConfigProtocol
from .logger import reptor_logger


class Config(ConfigProtocol):
    _raw_config: dict = {
        "server": "https://demo.sysre.pt",
        "token": None,
        "project_id": None,
        "community": False,
    }

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

    def get(self, key: str, default: typing.Optional[typing.Any] = None, plugin: str = None) -> typing.Any:
        """Returns a value from the current config

        Args:
            key (_type_): _description_
            default (typing.Any, optional): _description_. Defaults to None.

        Returns:
            typing.Any: _description_
        """
        if plugin:
            return self._raw_config.get(plugin, dict()).get(key, default)
        else:
            return self._raw_config.get(key, default)

    def get_config_keys(self, plugin: str = None) -> typing.Collection:
        if plugin:
            return self._raw_config.get(plugin, dict()).keys()
        else:
            return self._raw_config.keys()

    def set(self, key, value):
        """Sets a value in the config

        Args:
            key (_type_): _description_
            value (_type_): _description_
        """
        self._raw_config.update({key: value})

    def load_config(self):
        """Loads config file from user home directory"""
        if not settings.PERSONAL_SYSREPTOR_HOME.exists():
            reptor_logger.highlight(
                "No .sysreptor folder found in home directory...Creating one"
            )
            # exist_ok=True because logger might be faster, when creating log file and parents=True
            settings.PERSONAL_SYSREPTOR_HOME.mkdir(exist_ok=True)
        try:
            with open(settings.PERSONAL_CONFIG_FILE, "r") as f:
                self._raw_config = yaml.safe_load(f.read())
        except FileNotFoundError:
            pass

    def get_config_from_user(self):
        """Asks the user for the individiual settings and offers to
        write them into a config file
        """
        default_server = self._raw_config.get("server")
        self._raw_config["server"] = (
            input(f"Server [{default_server}]: ") or default_server
        )

        default_api_token = self._raw_config.get("token")
        self._raw_config["token"] = input(
            f"API Token{ f' [{default_api_token}]' if default_api_token else ''}: "
        ) or self._raw_config.get("token")

        default_project_id = self._raw_config.get("project_id")
        self._raw_config["project_id"] = (
            input(
                f"Project ID{ f' [{default_project_id}]' if default_project_id else ''}: "
            )
            or default_project_id
        )

        default_community_enabled = self._raw_config.get("community")
        is_community_enabled = "No"
        if default_community_enabled:
            is_community_enabled = "Yes"

        community = input(
            f"Enable Community Plugins?{ f'[Currently: {is_community_enabled}]'} [y/n]: "
        )[:1].lower()
        if community == 'y':
            self._raw_config["community"] = True
        elif community == 'n':
            self._raw_config["community"] = False

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

    def _write_to_file(self):
        """Writes config file as yaml file"""
        if self._raw_config:
            settings.PERSONAL_SYSREPTOR_HOME.mkdir(exist_ok=True)
            with open(settings.PERSONAL_CONFIG_FILE, "w") as f:
                filtered_config = {
                    k: v
                    for k, v in self._raw_config.items()
                    if k not in self._ignored_keys_in_config
                }
                yaml.dump(filtered_config, f, encoding="utf-8")
        else:
            raise ValueError("No config is currently set")

    def get_server(self) -> str:
        return self.get("server")

    def get_token(self) -> str:
        return self.get("token")

    def get_project_id(self) -> str:
        return self.get("project_id")

    def get_cli_overwrite(self) -> typing.Dict:
        return self.get("cli")

    def get_community_enabled(self) -> bool:
        return self.get("community")
