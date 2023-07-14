import typing
from abc import abstractmethod


class PluginManagerProtocol(typing.Protocol):
    LOADED_PLUGINS: typing.Dict = dict()

    @abstractmethod
    def run_loading_sequence(self) -> None:
        ...

    @abstractmethod
    def load_plugins(self):
        ...
