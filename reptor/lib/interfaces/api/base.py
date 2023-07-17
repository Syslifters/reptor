import typing
from abc import abstractmethod


class BaseApiProtocol(typing.Protocol):
    project_id: str
