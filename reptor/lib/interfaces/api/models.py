import typing
from abc import abstractmethod


class ProjectProtocol(typing.Protocol):
    name: str
    readonly: bool
    id: str


class ProjectDesignProtocol(typing.Protocol):
    ...


class NoteProtocol(typing.Protocol):
    ...


class FindingProtocol(typing.Protocol):
    ...


class SectionProtocol(typing.Protocol):
    ...
