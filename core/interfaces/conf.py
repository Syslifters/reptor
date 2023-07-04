import typing
from abc import abstractmethod


class ConfigProtocol(typing.Protocol):
    @abstractmethod
    def get(self, key: str, value: typing.Optional[typing.Any] = None) -> typing.Any:
        ...

    @abstractmethod
    def set(self) -> None:
        ...
