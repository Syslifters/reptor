import itertools
import typing
from typing import Any

from reptor.models.Base import BaseModel, ProjectFieldTypes
from reptor.settings import DEFAULT_PROJECT_DESIGN


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

    id: str = ""
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

    @property
    def name(self):
        return self.id

    def _fill_from_api(self, data: typing.Dict):
        data = data.copy()
        if 'id' not in data and 'name' in data:
            data['id'] = data['name']

        if data["type"] == ProjectFieldTypes.list.value:
            if isinstance(data["items"], dict):
                data["items"] = ProjectDesignField(data["items"])
        elif data["type"] == ProjectFieldTypes.object.value:
            if isinstance(data["properties"], dict):
                data["properties"] = [ProjectDesignField(f | {'id': fid}) for fid, f in data["properties"].items()]
            elif isinstance(data['properties'], list):
                data["properties"] = [ProjectDesignField(f) for f in data["properties"]]

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
            if isinstance(data.get("report_fields"), str):
                raise ValueError(
                    "report_fields should be list. Use ProjectDesignOverview instead."
                )
            if isinstance(data.get("finding_fields"), str):
                raise ValueError(
                    "finding_fields should be list. Use ProjectDesignOverview instead."
                )
        super().__init__(data)

    def _fill_from_api(self, data: typing.Dict):
        report_fields = []
        if isinstance(data.get('report_fields'), dict):
            report_fields = [ProjectDesignField(f | {'id': fid}) for fid, f in data['report_fields'].items()]
        else:
            for field in itertools.chain(*map(lambda s: s['fields'], data.get('report_sections', []))):
                if isinstance(field, dict):
                    report_fields.append(ProjectDesignField(field))
        
        finding_fields = []
        if isinstance(data.get('finding_fields'), dict):
            finding_fields = [ProjectDesignField(f | {'id': fid}) for fid, f in data['finding_fields'].items()]
        elif isinstance(data.get('finding_fields'), list):
            finding_fields = [ProjectDesignField(f) for f in data['finding_fields']]

        super()._fill_from_api(data | {'report_fields': report_fields, 'finding_fields': finding_fields})


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
