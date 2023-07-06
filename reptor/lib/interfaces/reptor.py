import typing
from abc import abstractmethod

from .conf import ConfigProtocol
from reptor.lib.logger import ReptorAdapter
from reptor.lib.console import Console


class ReptorProtocol(typing.Protocol):
    logger: ReptorAdapter
    console: Console

    @abstractmethod
    def get_config(self) -> ConfigProtocol:
        ...
