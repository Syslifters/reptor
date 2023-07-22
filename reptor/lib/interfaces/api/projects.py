import pathlib
import typing
from abc import abstractmethod
from .base import BaseApiProtocol

from .models import ProjectProtocol, FindingProtocol


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

    @abstractmethod
    def get_project(self) -> ProjectProtocol:
        ...

    @abstractmethod
    def get_findings(self) -> typing.List[FindingProtocol]:
        ...

    @abstractmethod
    def update_project(self, data: dict) -> None:
        ...

    @abstractmethod
    def update_finding(self, finding_id: str, data: dict) -> None:
        ...

    @abstractmethod
    def get_enabled_language_codes(self) -> list:
        ...
