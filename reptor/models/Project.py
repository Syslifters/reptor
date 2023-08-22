from reptor.models.Base import BaseModel
from reptor.models.User import User

import typing

from reptor.lib.interfaces.api.models import ProjectProtocol


class Project(BaseModel, ProjectProtocol):
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
    members: typing.List[User] = []
