import pathlib
import typing
from abc import abstractmethod

from .base import BaseApiProtocol
from .models import FindingProtocol, ProjectProtocol, SectionProtocol


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
    def get_sections(self) -> typing.List[SectionProtocol]:
        ...

    @abstractmethod
    def update_project(self, data: dict) -> dict:
        ...

    @abstractmethod
    def update_finding(self, finding_id: str, data: dict) -> dict:
        ...

    def update_section(self, section_id: str, data: dict) -> dict:
        ...

    @abstractmethod
    def get_enabled_language_codes(self) -> list:
        ...
