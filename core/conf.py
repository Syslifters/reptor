import os
import typing

import yaml
from .interfaces.conf import ConfigProtocol

config_path = os.path.join(os.path.expanduser("~"), ".sysreptor/config.yaml")


# config = load_config()
class Config(ConfigProtocol):
    _raw_config: dict = {
        "server": "https://demo.sysre.pt",
        "token": None,
        "project_id": None,
    }

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def get(self, key, default: typing.Any = None) -> typing.Any:
        return self.instance._raw_config.get(key, default)

    def set(self, key, value):
        self.instance._raw_config.update({key: value})

    def load_config(self):
        try:
            with open(config_path, "r") as f:
                self._raw_config = yaml.safe_load(f.read())
        except FileNotFoundError:
            pass

    def get_config_from_user(self):
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
        store = None
        while store not in ["y", "n"]:
            store = input("Store to config to ~/.sysreptor/config.yaml? [y/n]: ")
        if store == "y":
            self._write_to_file()

    def _write_to_file(self):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(self._raw_config, f, encoding="utf-8")
