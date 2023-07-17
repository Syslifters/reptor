import typing
from abc import abstractmethod


class ProjectProtocol(typing.Protocol):
    name: str
    readonly: bool
    id: str


class NoteProtocol(typing.Protocol):
    ...
