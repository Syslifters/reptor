import os
import typing

import yaml
from .interfaces.conf import ConfigProtocol

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".sysreptor/config.yaml")


class Config(ConfigProtocol):
    _raw_config: dict = {
        "server": "https://demo.sysre.pt",
        "token": None,
        "project_id": None,
    }

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

    def get(self, key, default: typing.Any = None) -> typing.Any:
        """Returns a value from the current config

        Args:
            key (_type_): _description_
            default (typing.Any, optional): _description_. Defaults to None.

        Returns:
            typing.Any: _description_
        """
        return self._raw_config.get(key, default)

    def set(self, key, value):
        """Sets a value in the config

        Args:
            key (_type_): _description_
            value (_type_): _description_
        """
        self._raw_config.update({key: value})

    def load_config(self):
        """Loads config file from user home directory"""
        try:
            with open(CONFIG_PATH, "r") as f:
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
        self.store_config()

    def store_config(self):
        """Offer user to write temporary config to local config file"""
        store = None
        while store not in ["y", "n"]:
            store = input("Store to config to ~/.sysreptor/config.yaml? [y/n]: ")
        if store == "y":
            self._write_to_file()
        self.instance._raw_config = self._raw_config

    def _write_to_file(self):
        """Writes config file as yaml file"""
        if self._raw_config:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                yaml.dump(self._raw_config, f, encoding="utf-8")
        else:
            raise ValueError("No config is currently set")
