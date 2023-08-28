import typing

from reptor.models.Base import BaseModel
from reptor.models.Finding import Finding
from reptor.models.Section import Section
from reptor.models.User import User


class Project(BaseModel):
    """
    Attributes:
        name:
        project_type:
        language:
        tags:
        readonly:
        source:
        copy_of:
        members:
    """

    name: str = ""

    project_type: str = ""  # is the project design id

    language: str = ""
    tags: typing.List[str] = []
    readonly: bool = False
    source: str = ""
    copy_of: str = ""
    override_finding_order: bool = False
    members: typing.List[User] = []
    imported_members: typing.List[User] = []
    details: str = ""
    notes: str = ""
    images: str = ""
    findings: typing.List[Finding] = []
    sections: typing.List[Section] = []
