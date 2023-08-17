from reptor.models.Base import BaseModel
from reptor.models.User import User
from reptor.models.Base import ProjectFieldTypes


import typing
from typing import Any

from reptor.lib.interfaces.api.models import ProjectDesignProtocol, ProjectProtocol


class ProjectDesignField(BaseModel):
    """

    Attributes:
        name:
        type:
        label:
        origin:
        default:
        required:
        spellcheck:

        properties: "ProjectDesignField"
        choices:
        items:
        suggestions:
    """

    name: str = ""
    type: ProjectFieldTypes
    label: str = ""
    origin: str = ""
    default: str = ""
    required: bool = False
    spellcheck: bool = False
    # Use Any instead of "typing.List['ProjectDesignField'] = []" due to Python bug
    # See: https://bugs.python.org/issue44926
    properties: Any = None
    choices: typing.List[dict] = []
    items: dict = {}
    suggestions: typing.List[str] = []

    def _fill_from_api(self, data: typing.Dict):
        if data["type"] == ProjectFieldTypes.list.value:
            data["items"] = ProjectDesignField(data["items"])
        elif data["type"] == ProjectFieldTypes.object.value:
            properties = list()
            for name, field in data["properties"].items():
                field["name"] = name
                properties.append(ProjectDesignField(field))
            data["properties"] = properties

        attrs = typing.get_type_hints(self).keys()
        for key, value in data.items():
            if key in attrs:
                self.__setattr__(key, value)


class ProjectDesign(BaseModel, ProjectDesignProtocol):
    """
    Attributes:
        source:
        scope:
        name:
        language:
        report_fields:
        finding_fields:
    """

    source: str = ""
    scope: str = ""
    name: str = ""
    language: str = ""
    report_fields: typing.List[ProjectDesignField] = []
    finding_fields: typing.List[ProjectDesignField] = []


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
