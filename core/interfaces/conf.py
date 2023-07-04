import typing
from abc import abstractmethod


class ConfigProtocol(typing.Protocol):
    @abstractmethod
    def get(self):
        ...

    @abstractmethod
    def set(self):
        ...
