import typing
from abc import abstractmethod

from .conf import ConfigProtocol


class ReptorProtocol(typing.Protocol):
    @abstractmethod
    def get_config(self) -> ConfigProtocol:
        ...
