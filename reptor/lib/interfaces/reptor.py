import typing
from abc import abstractmethod

from reptor.lib.console import Console
from reptor.lib.logger import ReptorAdapter
from reptor.lib.interfaces.pluginmanager import PluginManagerProtocol

from .conf import ConfigProtocol


class ReptorProtocol(typing.Protocol):
    logger: ReptorAdapter
    console: Console
    plugin_manager: PluginManagerProtocol

    @abstractmethod
    def get_config(self) -> ConfigProtocol:
        ...

    @abstractmethod
    def get_logger(self) -> ReptorAdapter:
        ...

    @abstractmethod
    def get_plugin_manager(self) -> PluginManagerProtocol:
        ...
