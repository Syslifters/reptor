import copy
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
        type (str): Field type (string, enum, list, object, etc.).
        label (str): Human-readable field label.
        origin (str): Source origin of the field.
        default (Any): Default value for the field.
        required (bool): Whether the field is required.
        spellcheck (bool): Whether spellcheck is enabled for this field.
        properties (Any): Nested field properties for object types.
        choices (List[dict]): Available choices for enum fields.
        items (Any): Item definition for list fields.
        suggestions (List[str]): List of suggested values for the field.
        pattern (str): Regular expression pattern for validation (used for fields in project designs).
        help_text (str): Help text for the field.
        cvss_version (str): CVSS version constraint for cvss fields.
        minimum (Any): Minimum value for number fields.
        maximum (Any): Maximum value for number fields.
        schema (dict): JSON schema for json fields.

    Methods:
        to_dict(): Convert to a dictionary representation.
        to_api_dict(): Convert to SysReptor API field definition format.
    """
    id: str = ""  # Keep this definition (even though also inherited); otherwise, init breaks
    type: str
    label: str = ""
    origin: str = ""
    default: Any = None
    required: bool = False
    spellcheck: bool = False
    # Use Any instead of "typing.List['ProjectDesignField'] = []" due to Python bug
    # See: https://bugs.python.org/issue44926
    properties: Any = None
    choices: typing.List[dict] = []
    items: Any = None
    suggestions: typing.List[str] = []
    pattern: typing.Optional[str] = None
    help_text: typing.Optional[str] = None
    cvss_version: typing.Optional[str] = None
    minimum: Any = None
    maximum: Any = None
    schema: typing.Optional[dict] = None

    @property
    def name(self):
        return self.id

    def _field_type_str(self) -> str:
        if isinstance(self.type, ProjectFieldTypes):
            return self.type.value
        return str(self.type)

    def _fill_from_api(self, data: typing.Dict):
        data = data.copy()
        if 'id' not in data and 'name' in data:
            data['id'] = data['name']

        field_type = data["type"].value if isinstance(data["type"], ProjectFieldTypes) else data["type"]

        if field_type == ProjectFieldTypes.list.value:
            if isinstance(data.get("items"), dict):
                data["items"] = ProjectDesignField(data["items"])
        elif field_type == ProjectFieldTypes.object.value:
            if isinstance(data.get("properties"), dict):
                data["properties"] = [ProjectDesignField(f | {'id': fid}) for fid, f in data["properties"].items()]
            elif isinstance(data.get('properties'), list):
                data["properties"] = [ProjectDesignField(f) for f in data["properties"]]

        attrs = typing.get_type_hints(self.__class__).keys()
        for key, value in data.items():
            if key in attrs:
                self.__setattr__(key, value)

    def to_api_dict(self, *, include_id: bool = True) -> dict:
        """Serialize to SysReptor field definition format for API writes."""
        field_type = self._field_type_str()
        result: dict[str, Any] = {"type": field_type}

        if include_id and self.id:
            result["id"] = self.id
        if self.label:
            result["label"] = self.label
        if self.origin:
            result["origin"] = self.origin
        if self.help_text is not None:
            result["help_text"] = self.help_text

        if field_type == "user":
            result["required"] = self.required
            return result

        result["required"] = self.required

        if field_type in {"string", "markdown", "date", "cvss", "cwe", "enum", "combobox", "number", "boolean", "json"}:
            result["default"] = self.default

        if field_type == "string":
            result["spellcheck"] = self.spellcheck
            if self.pattern is not None:
                result["pattern"] = self.pattern
        elif field_type == "cvss" and self.cvss_version is not None:
            result["cvss_version"] = self.cvss_version
        elif field_type == "enum":
            result["choices"] = self.choices
        elif field_type == "combobox":
            result["suggestions"] = self.suggestions
        elif field_type == "number":
            result["minimum"] = self.minimum
            result["maximum"] = self.maximum
        elif field_type == "json" and self.schema is not None:
            result["schema"] = self.schema
        elif field_type == "object":
            result["properties"] = [
                (prop if isinstance(prop, ProjectDesignField) else ProjectDesignField(prop)).to_api_dict()
                for prop in (self.properties or [])
            ]
        elif field_type == "list":
            if self.items is not None:
                items = self.items if isinstance(self.items, ProjectDesignField) else ProjectDesignField(self.items)
                result["items"] = items.to_api_dict(include_id=bool(items.id))

        return result

    def __str__(self):
        return self.id
    
    def __repr__(self):
        return f'ProjectDesignField(name="{self.id}", label="{self.label}", type="{self.type}")'


def merge_report_fields_into_sections(
    report_sections: typing.List[dict],
    report_fields: typing.List[ProjectDesignField],
) -> typing.List[dict]:
    """Merge flat report field definitions into report_sections for API updates."""
    field_map = {field.id: field.to_api_dict() for field in report_fields}
    sections = copy.deepcopy(report_sections)
    seen_ids: set[str] = set()

    for section in sections:
        updated_fields = []
        for field in section.get("fields", []):
            field_id = field.get("id") if isinstance(field, dict) else None
            if field_id and field_id in field_map:
                updated_fields.append(field_map[field_id])
                seen_ids.add(field_id)
            else:
                updated_fields.append(field)
        section["fields"] = updated_fields

    new_field_ids = set(field_map.keys()) - seen_ids
    if new_field_ids:
        other_section = next((section for section in sections if section.get("id") == "other"), None)
        if other_section is None:
            other_section = {"id": "other", "label": "Other", "fields": []}
            sections.append(other_section)
        for field_id in new_field_ids:
            other_section["fields"].append(field_map[field_id])

    return sections


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
        report_template (str): Report design HTML source.
        report_styles (str): Report CSS styles.
        report_sections (List[dict]): Report section definitions including embedded field definitions.
        finding_fields (List[ProjectDesignField]): List of field definitions for findings.
        report_fields (List[ProjectDesignField]): List of field definitions for report sections (derived from `report_sections` received from the API).
        report_preview_data (dict): Preview data for report design.
        
    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    copy_of: str = ""
    
    report_template: str = ""
    report_styles: str = ""
    report_sections: typing.List[dict] = []
    finding_fields: typing.List[ProjectDesignField] = []
    report_fields: typing.List[ProjectDesignField] = []
    report_preview_data: dict = {}

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
