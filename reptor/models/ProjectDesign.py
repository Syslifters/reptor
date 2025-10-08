import itertools
import typing
from typing import Any

from reptor.models.Base import BaseModel, ProjectFieldTypes
from reptor.settings import DEFAULT_PROJECT_DESIGN


class ProjectDesignField(BaseModel):
    """
    Represents a field definition in a project design template.

    Attributes:
        id (str): Field identifier/name.
        type (ProjectFieldTypes): Field type (string, enum, list, object, etc.).
        label (str): Human-readable field label.
        origin (str): Source origin of the field.
        default (str): Default value for the field.
        required (bool): Whether the field is required.
        spellcheck (bool): Whether spellcheck is enabled for this field.
        properties (Any): Nested field properties for object types.
        choices (List[dict]): Available choices for enum fields.
        items (dict): Item definition for list fields.
        suggestions (List[str]): List of suggested values for the field.
        pattern (str): Regular expression pattern for validation (used for fields in project designs).
        help_text (str): Help text for the field.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    id: str = ""  # Keep this definition (even though also inherited); otherwise, init breaks
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
    pattern: str = ""
    help_text: str = ""

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

        attrs = typing.get_type_hints(self.__class__).keys()
        for key, value in data.items():
            if key in attrs:
                self.__setattr__(key, value)

    def __str__(self):
        return self.id
    
    def __repr__(self):
        return f'ProjectDesignField(name="{self.id}", label="{self.label}", type="{self.type}")'


class ProjectDesignBase(BaseModel):
    source: str = ""
    scope: str = ""
    name: str = ""
    tags: typing.List[str] = []
    language: str = ""
    usage_count: int = 0

    details: str = ""
    assets: str = ""

    def __init__(self, data: typing.Optional[typing.Dict] = None):
        if data is None:
            data = DEFAULT_PROJECT_DESIGN
        super().__init__(data)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'{self.__class__.__name__}(name="{self.name}", id="{self.id}")'


class ProjectDesign(ProjectDesignBase):
    """
    Project design template with incl. field definitions and default values.

    Attributes:
        id (str): Project design ID (uuid).
        created (datetime): Date when the project design was created.
        updated (datetime): Date when the project design was last updated.
        
        source (str): Source of the project design. Possible values: `created`, `imported`, `imported_dependecy`, `customized`, `snapshot`.
        scope (str): Scope of the project design (e.g., "global", "user").
        name (str): Project design name.
        tags (List[str]): List of tags associated with the project design.
        language (str): Language code for the project design (e.g., "en-US").
        usage_count (int): Counts how often the project design has been assigned to a project.
        details (str): Project design details API endpoint (URL).
        assets (str): Project design assets API endpoint (URL).

        copy_of (str): ID of the original project design this is a copy of (if any).
        finding_fields (List[ProjectDesignField]): List of field definitions for findings.
        report_fields (List[ProjectDesignField]): List of field definitions for report sections (derived from `report_sections` received from the API).

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    copy_of: str = ""
    
    finding_fields: typing.List[ProjectDesignField] = []
    report_fields: typing.List[ProjectDesignField] = []

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
    """    
    `ProjectDesignOverview` has the same base attributes as `ProjectDesign`, except for `copy_of`, `report_fields` and `finding_fields`.

    Attributes:
        id (str): Project design ID (uuid).
        created (datetime): Date when the project design was created.
        updated (datetime): Date when the project design was last updated.
        
        source (str): Source of the project design. Possible values: `created`, `imported`, `imported_dependecy`, `customized`, `snapshot`.
        scope (str): Scope of the project design (e.g., "global", "user").
        name (str): Project design name.
        tags (List[str]): List of tags associated with the project design.
        language (str): Language code for the project design (e.g., "en-US").
        usage_count (int): Counts how often the project design has been assigned to a project.
        details (str): Project design details API endpoint (URL).
        assets (str): Project design assets API endpoint (URL).

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
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
