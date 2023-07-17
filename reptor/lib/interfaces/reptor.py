import typing
from abc import abstractmethod

from reptor.lib.console import Console
from reptor.lib.logger import ReptorAdapter
from reptor.lib.interfaces.pluginmanager import PluginManagerProtocol
from reptor.lib.interfaces.apimanager import APIManagerProtocol

from .conf import ConfigProtocol


class ReptorProtocol(typing.Protocol):
    logger: ReptorAdapter
    console: Console
    plugin_manager: PluginManagerProtocol
    api: APIManagerProtocol
    is_community_enabled: bool

    @abstractmethod
    def get_config(self) -> ConfigProtocol:
        ...

    @abstractmethod
    def get_logger(self) -> ReptorAdapter:
        ...

    @abstractmethod
    def get_plugin_manager(self) -> PluginManagerProtocol:
        ...
