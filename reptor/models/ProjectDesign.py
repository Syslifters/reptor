from typing import Any
from reptor.models.Base import BaseModel, ProjectFieldTypes
from reptor.settings import DEFAULT_PROJECT_DESIGN


import typing


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
            if isinstance(data["items"], dict):
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


class ProjectDesignBase(BaseModel):
    source: str = ""
    scope: str = ""
    name: str = ""
    language: str = ""

    def __init__(self, data: typing.Optional[typing.Dict] = None):
        if data is None:
            data = DEFAULT_PROJECT_DESIGN
        super().__init__(data)


class ProjectDesign(ProjectDesignBase):
    report_fields: typing.List[ProjectDesignField] = []
    finding_fields: typing.List[ProjectDesignField] = []

    def __init__(self, data: typing.Optional[typing.Dict] = None):
        if data:
            if isinstance(data.get("report_fields"), list):
                raise ValueError(
                    "report_fields should be list. Use ProjectDesignOverview instead."
                )
            if isinstance(data.get("finding_fields"), list):
                raise ValueError(
                    "finding_fields should be list. Use ProjectDesignOverview instead."
                )
        super().__init__(data)


class ProjectDesignOverview(ProjectDesignBase):
    report_fields: str = ""
    finding_fields: str = ""

    def __init__(self, data: typing.Optional[typing.Dict] = None):
        if data:
            if isinstance(data.get("report_fields"), list):
                raise ValueError(
                    "report_fields should be str. Use ProjectDesign instead."
                )
            if isinstance(data.get("finding_fields"), list):
                raise ValueError(
                    "finding_fields should be str. Use ProjectDesign instead."
                )
        super().__init__(data)
