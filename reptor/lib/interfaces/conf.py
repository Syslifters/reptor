import typing
from abc import abstractmethod


class ConfigProtocol(typing.Protocol):
    @abstractmethod
    def get_config_from_user(self):
        ...

    @abstractmethod
    def get(self, key: str, default: typing.Optional[typing.Any] = None, plugin: str = None) -> typing.Any:
        ...

    @abstractmethod
    def get_config_keys(self, plugin: str = None) -> typing.Collection:
        ...

    @abstractmethod
    def set(self) -> None:
        ...

    @abstractmethod
    def get_server(self) -> str:
        ...

    @abstractmethod
    def get_token(self) -> str:
        ...

    @abstractmethod
    def get_project_id(self) -> str:
        ...

    @abstractmethod
    def get_cli_overwrite(self) -> typing.Dict:
        ...

    @abstractmethod
    def get_community_enabled(self) -> bool:
        ...
