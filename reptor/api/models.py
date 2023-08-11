import datetime
import enum
import sys
import typing
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from reptor.lib.interfaces.api.models import (
    FindingProtocol,
    ProjectDesignProtocol,
    ProjectProtocol,
    SectionProtocol,
)


class ProjectFieldTypes(enum.Enum):
    cvss = "cvss"
    string = "string"
    markdown = "markdown"
    list = "list"
    object = "object"
    enum = "enum"
    user = "user"
    combobox = "combobox"
    date = "date"
    number = "number"
    boolean = "boolean"


class FindingTemplateSources(enum.Enum):
    CREATED = "created"
    IMPORTED = "imported"
    IMPORTED_DEPENDENCY = "imported_dependency"
    CUSTOMIZED = "customized"
    SNAPSHOT = "snapshot"


@dataclass
class BaseModel:
    """
    Base Model
    """

    id: str = ""
    created: datetime.datetime = datetime.datetime.now()
    updated: datetime.datetime = datetime.datetime.now()

    def __init__(self, data: typing.Optional[typing.Dict] = None):
        if data:
            self._fill_from_api(data)

    def _get_combined_class_type_hints(self) -> dict:
        type_hints = list()
        type_hints_from_class = self.__class__
        while type_hints_from_class.__base__:
            type_hints.append(typing.get_type_hints(type_hints_from_class))
            if type_hints_from_class == BaseModel:
                break
            type_hints_from_class = type_hints_from_class.__base__

        combined_class_type_hints = dict()
        for type_hint in reversed(type_hints):
            combined_class_type_hints.update(type_hint)
        return combined_class_type_hints

    def _fill_from_api(self, data: typing.Dict):
        """Fills Model from reptor.api return JSON data

        Args:
            data (str): API Return Data
        """
        combined_class_type_hints = self._get_combined_class_type_hints()

        for attr in combined_class_type_hints.items():
            if attr[0] in data:
                # Check if one of our models, then proceed recursively
                try:
                    model_class = attr[1]._name
                except AttributeError:
                    model_class = attr[1].__name__

                is_list = False
                if model_class == "List":
                    model_class = attr[1].__args__[0].__name__
                    is_list = True

                if model_class in [
                    "User",
                    "FindingTemplate",
                    "FindingDataRaw",
                    "SectionDataRaw",
                    "Note",
                    "Project",
                    "ProjectDesign",
                    "FindingTemplateTranslation",
                ]:
                    cls = getattr(sys.modules[__name__], model_class)

                    if is_list:
                        item_list = list()
                        for item in data[attr[0]]:
                            item_list.append(cls(item))
                        self.__setattr__(attr[0], item_list)
                    else:
                        self.__setattr__(attr[0], cls(data[attr[0]]))
                elif model_class in ["ProjectDesignField"]:
                    cls = getattr(sys.modules[__name__], model_class)
                    self.__setattr__(attr[0], list())
                    for k, v in data[attr[0]].items():
                        v["name"] = k
                        self.__getattribute__(attr[0]).append(cls(v))
                else:
                    # Fill each attribute
                    self.__setattr__(attr[0], data[attr[0]])

    def to_json(self):
        # data = {}
        # for key, value in self.__dict__.items():
        #    if key not in ["created", "updated"]:
        #        data.update({key: value})
        # return data
        return self.__dict__


class User(BaseModel):
    """
    Attributes:
        username:
        name:
        title_before:
        first_name:
        middle_name:
        last_name:
        title_after:
        is_active:
        roles:
        email:
        phone:
        mobile:
        scope:
        is_superuser:
        is_designer:
        is_template_editor:
        is_guest:
        is_user_manager:
        is_system_user:
        is_global_archiver:
        is_mfa_enabled:
        can_login_local:
        can_login_sso:
    """

    username: str = ""
    name: str = ""
    title_before: str = ""
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    title_after: str = ""
    is_active: bool = False
    roles: typing.List[str] = []
    email: str = ""
    phone: str = ""
    mobile: str = ""
    scope: typing.List[str] = []
    is_superuser: bool = False
    is_designer: bool = False
    is_template_editor: bool = False
    is_guest: bool = False
    is_user_manager: bool = False
    is_system_user: bool = False
    is_global_archiver: bool = False
    is_mfa_enabled: bool = False
    can_login_local: bool = False
    can_login_sso: bool = False


class SectionDataRaw(BaseModel):
    def _fill_from_api(self, data: typing.Dict):
        """Fills Model from reptor.api return JSON data
        For FindingDataRaw, undefined keys should also be set.

        Args:
            data (str): API Return Data
        """
        for key, value in data.items():
            # We don't care about recursion here
            self.__setattr__(key, value)


class FindingDataRaw(SectionDataRaw):
    """
    Custom finding fields will be added as additional attributes.

    Attributes:
        title:
        cvss:
        summary:
        description:
        precondition:
        impact:
        recommendation:
        short_recommendation:
        references:
        affected_components:
        owasp_top10_2021:
        wstg_category:
        retest_notes:
        retest_status:
        evidence:
    """

    title: str = ""
    cvss: str = ""
    summary: str = ""
    description: str = ""
    precondition: str = ""
    impact: str = ""
    recommendation: str = ""
    short_recommendation: str = ""
    references: typing.List[str] = []
    affected_components: typing.List[str] = []
    owasp_top10_2021: str = ""
    wstg_category: str = ""
    retest_notes: str = ""
    retest_status: str = ""
    evidence: str = ""

    def to_json(self) -> dict:
        return self.__dict__


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


class SectionDataField(ProjectDesignField):
    """
    Section data holds values only and does not contain type definitions.
    Most data types cannot be differentiated (like strings and enums).

    This model joins finding data values from an acutal report with project
    design field definitions.
    """

    value: typing.Union[
        str,  # cvss, string, markdown, enum, user, combobox, date
        typing.List,  # list
        bool,  # boolean
        float,  # number
        Any,  # "SectionDataField" for object
    ]

    def __init__(
        self,
        design_field: ProjectDesignField,
        value: typing.Union[
            str,
            typing.List,
            bool,
            float,
            Any,
        ],
    ):
        # Set attributes from ProjectDesignField
        project_design_type_hints = typing.get_type_hints(ProjectDesignField)
        for attr in project_design_type_hints.items():
            self.__setattr__(attr[0], design_field.__getattribute__(attr[0]))

        if self.type == ProjectFieldTypes.object.value:
            property_value = dict()
            for property in self.properties:
                # property is of type ProjectDesignField
                try:
                    property_value[property.name] = self.__class__(
                        property, value[property.name]
                    )

                except KeyError:
                    raise KeyError(
                        f"Object name '{property.name}' not found. Did you mix"
                        f"mismatched project design with project data?"
                    )
            self.value = property_value
        elif self.type == ProjectFieldTypes.list.value:
            self.value = list()
            for v in value:  # type: ignore
                self.value.append(self.__class__(self.items, v))  # type: ignore
        else:
            self.value = value

    def __iter__(self):
        """Recursive iteration through potentially nested SectionDataFields
        returns iterator of SectionDataField"""
        if self.type == ProjectFieldTypes.list.value:
            yield self  # First yield self, then nested fields
            # Iterate through list
            for field in self.value:  # type: ignore
                # Iterate through field for recursion
                for f in field:
                    yield f
        elif self.type == ProjectFieldTypes.object.value:
            yield self  # First yield self, then nested fields
            for _, field in self.value.items():  # type: ignore
                for f in field:
                    yield f
        else:
            yield self

    def __len__(self) -> int:
        return len([e for e in self])

    def to_json(self) -> typing.Union[dict, list, str]:
        if self.type == ProjectFieldTypes.list.value:
            result = list()
            for subfield in self.value:
                if subfield.type == ProjectFieldTypes.enum.value:
                    result.append({subfield.name: subfield.value})
                else:
                    result.append(subfield.to_json())
        elif self.type == ProjectFieldTypes.object.value:
            result = dict()
            for name, subfield in self.value.items():
                if subfield.type == ProjectFieldTypes.enum.value:
                    result[name] = {subfield.name: subfield.value}
                result[name] = subfield.to_json()
        else:
            return self.value
        return result

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "value" and __value is not None:
            if self.type in [
                ProjectFieldTypes.combobox.value,
                ProjectFieldTypes.cvss.value,
                ProjectFieldTypes.string.value,
                ProjectFieldTypes.markdown.value,
            ]:
                if not isinstance(__value, str):
                    raise ValueError(
                        f"'{self.name}' expects a string value (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.date.value:
                try:
                    datetime.datetime.strptime(__value, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        f"'{self.name}' expects date in format 2000-01-01 (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.enum.value:
                valid_enums = [choice["value"] for choice in self.choices]
                if __value not in valid_enums:
                    raise ValueError(
                        f"'{__value}' is not an valid enum choice for '{self.name}'."
                    )
            elif self.type == ProjectFieldTypes.list.value:
                if not isinstance(__value, list):
                    raise ValueError(
                        f"Value of '{self.name}' must be list  (got '{type(__value)}')."
                    )
                if not all([isinstance(v, self.__class__) for v in __value]):
                    raise ValueError(
                        f"Value of '{self.name}' must contain list of {self.__class__.__name__}."
                    )
                types = set([v.type for v in __value])
                if len(types) > 1:
                    raise ValueError(
                        f"Values of '{self.name}' must not contain {self.__class__.__name__}s"
                        f"of multiple types (got {','.join(types)})."
                    )
            elif self.type == ProjectFieldTypes.object.value:
                if not isinstance(__value, dict):
                    raise ValueError(
                        f"Value of '{self.name}' must be dict (got '{type(__value)}')."
                    )
                for k, v in __value.items():
                    if not isinstance(v, self.__class__):
                        raise ValueError(
                            f"Value of '{self.name}' dict values must contain {self.__class__.__name__} "
                            f"(got '{type(v)}' for key '{k}')."
                        )
            elif self.type == ProjectFieldTypes.boolean.value:
                if not isinstance(__value, bool):
                    raise ValueError(
                        f"'{self.name}' expects a boolean value (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.number.value:
                if not isinstance(__value, int) and not isinstance(__value, float):
                    raise ValueError(
                        f"'{self.name}' expects int or float (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.user.value:
                try:
                    UUID(__value, version=4)
                except ValueError:
                    raise ValueError(
                        f"'{self.name}' expects v4 uuid (got '{__value}')."
                    )

        return super().__setattr__(__name, __value)


class FindingDataField(SectionDataField):
    ...


class SectionData(BaseModel):
    field_class = SectionDataField

    def __init__(
        self, design_fields: typing.List[ProjectDesignField], data_raw: SectionDataRaw
    ):
        for design_field in design_fields:
            try:
                value = data_raw.__getattribute__(design_field.name)
            except AttributeError:
                continue
            self.__setattr__(
                design_field.name,
                self.field_class(design_field, value),
            )

    def __iter__(self):
        """Recursive iteration through cls attributes
        returns FindingDataField"""
        for _, finding_field in self.__dict__.items():
            for nested_field in finding_field:
                yield nested_field

    def __len__(self) -> int:
        return len([e for e in self])

    def to_json(self) -> dict:
        result = dict()
        for key, value in self.__dict__.items():
            result[key] = value.to_json()
        return result


class FindingData(SectionData):
    title: FindingDataField
    cvss: FindingDataField
    summary: FindingDataField
    description: FindingDataField
    precondition: FindingDataField
    impact: FindingDataField
    recommendation: FindingDataField
    short_recommendation: FindingDataField
    references: FindingDataField
    affected_components: FindingDataField
    owasp_top10_2021: FindingDataField
    wstg_category: FindingDataField
    retest_notes: FindingDataField
    retest_status: FindingDataField
    evidence: FindingDataField

    field_class = FindingDataField

    def __init__(
        self, design_fields: typing.List[ProjectDesignField], data_raw: FindingDataRaw
    ):
        super().__init__(design_fields, data_raw)


class SectionRaw(BaseModel):
    """
    Attributes:
        project:
        project_type:
        language:
        lock_info:
        template:
        assignee:
        status:
        data:
    """

    project: str = ""
    project_type: str = ""
    language: str = ""
    lock_info: bool = False
    template: str = ""
    assignee: str = ""
    status: str = ""
    data: SectionDataRaw


class FindingRaw(SectionRaw):
    data: FindingDataRaw


class FindingTemplateTranslation(BaseModel):
    language: str = "en-US"
    status: str = "in-progress"
    is_main: bool = True
    data: FindingDataRaw

    def to_json(self) -> dict:
        result = self.__dict__
        result["data"] = self.data.to_json()
        return result


class FindingTemplate(BaseModel):
    """
    Attributes:
        details:
        images:
        lock_info:
        usage_count:
        source:
        tags:
        translations:
    """

    details: str = ""
    images: str = ""
    lock_info: bool = False
    usage_count: int = 0
    source: FindingTemplateSources = FindingTemplateSources.CREATED
    tags: typing.List[str] = []
    translations: typing.List[FindingTemplateTranslation] = []

    def to_json(self) -> dict:
        result = self.__dict__
        if isinstance(self.source, FindingTemplateSources):
            result["source"] = self.source.value
        result["translations"] = [t.to_json() for t in self.translations]
        return result


class Note(BaseModel):
    """
    Attributes:
        lock_info:
        title:
        text:
        checked:
        icon_emoji:
        status_emoji:
        order:
        parent:
    """

    lock_info: bool = False
    title: str = ""
    text: str = ""
    checked: bool = False
    icon_emoji: str = ""
    status_emoji: str = ""
    order: int = 0
    parent: str = ""


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


class Section(SectionRaw, SectionProtocol):
    data: SectionData

    def __init__(self, project_design: ProjectDesign, raw: SectionRaw):
        # Set attributes from FindingRaw
        for attr in typing.get_type_hints(SectionRaw).items():
            self.__setattr__(attr[0], raw.__getattribute__(attr[0]))

        self.data = SectionData(project_design.report_fields, raw.data)


class Finding(FindingRaw, FindingProtocol):
    data: FindingData

    def __init__(self, project_design: ProjectDesign, raw: FindingRaw):
        # Set attributes from FindingRaw
        for attr in typing.get_type_hints(FindingRaw).items():
            self.__setattr__(attr[0], raw.__getattribute__(attr[0]))

        self.data = FindingData(project_design.finding_fields, raw.data)


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
