import typing
from abc import abstractmethod

from .api.notes import ApiNotesProtocol
from .api.projects import ApiProjectsProtocol
from .api.templates import ApiTemplatesProtocol


class APIManagerProtocol(typing.Protocol):
    notes: ApiNotesProtocol
    projects: ApiProjectsProtocol
    templates: ApiTemplatesProtocol
