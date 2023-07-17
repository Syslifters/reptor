import pathlib
import typing
from abc import abstractmethod
from .base import BaseApiProtocol

from .models import ProjectProtocol


class ApiProjectsProtocol(BaseApiProtocol):
    project_id: str

    @abstractmethod
    def export(self, file_name: pathlib.Path):
        ...

    @abstractmethod
    def search(self, q: str) -> typing.List[ProjectProtocol]:
        ...

    @abstractmethod
    def duplicate(self) -> ProjectProtocol:
        ...

    @abstractmethod
    def get_projects(self) -> typing.List[ProjectProtocol]:
        ...
