from dataclasses import dataclass
import datetime
import sys
import typing
import enum
from reptor.lib.interfaces.api.models import ProjectProtocol


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
        basemodel_class_type_hints = typing.get_type_hints(BaseModel)
        current_class_type_hints = typing.get_type_hints(self)
        combined_class_type_hints = {
            **basemodel_class_type_hints,
            **current_class_type_hints,
        }
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
                    "FindingData",
                    "Note",
                    "Project",
                    "ProjectDesign",
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

    def _to_api_json(self):
        data = {}
        for key, value in self.__dict__.items():
            if key not in ["created", "updated"]:
                data.update({key: value})
        return data


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


class FindingData(BaseModel):
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

    def _fill_from_api(self, data: typing.Dict):
        """Fills Model from reptor.api return JSON data
        For FindingData, undefined keys should also be set.

        Args:
            data (str): API Return Data
        """
        super()._fill_from_api(data)
        for key, value in data.items():
            if not hasattr(self, key):
                self.__setattr__(key, value)
                # TODO what about nested data types?


class Finding(BaseModel):
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
    data: FindingData = None


class FindingTemplate(BaseModel):
    """
    Attributes:
        details:
        lock_info:
        usage_count:
        source:
        tags:
        language:
        status:
        data:
        custom_attributes:
    """

    details: str = ""
    lock_info: bool = False
    usage_count: int = 0
    source: str = ""
    tags: typing.List[str] = []
    language: str = ""
    status: str = ""
    data: FindingData = None


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


class ProjectFieldTypes(enum.Enum):
    cvss: str = "cvss"
    string: str = "string"
    markdown: str = "markdown"
    list: str = "list"
    object: str = "object"
    enum: str = "enum"
    user: str = "user"
    combobox: str = "combobox"
    date: str = "date"
    number: str = "number"
    boolean: str = "boolean"


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
    type: ProjectFieldTypes = None
    label: str = ""
    origin: str = ""
    default: str = ""
    required: bool = False
    spellcheck: bool = None
    # Use TypeAlias instead of "typing.List['ProjectDesignField'] = []" due to Python bug
    # See: https://bugs.python.org/issue44926
    properties: typing.TypeAlias = "ProjectDesignField"
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


class ProjectDesign(BaseModel):
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


class FindingDataField(BaseModel):
    """
    Finding data holds values only and does not contain type definitions.
    Most data types cannot be differentiated (like strings and enums).

    This model joins finding data values from an acutal report with project
    design field definitions.
    """

    value: typing.Union[
        str,  # cvss, string, markdown, enum, user, combobox, date
        typing.List,  # list
        bool,  # boolean
        int,  # number
        typing.TypeAlias,  # "FindingDataField" for object
    ]
    type: ProjectDesignField


class FindingDataJoined(BaseModel):
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

    def _fill_from_api(self, data: typing.Dict):
        """Fills Model from reptor.api return JSON data
        For FindingData, undefined keys should also be set.

        Args:
            data (str): API Return Data
        """
        super()._fill_from_api(data)
        for key, value in data.items():
            if not hasattr(self, key):
                self.__setattr__(key, value)
                # TODO what about nested data types?


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

    # Todo: should be ProjectType but API returns no object, but ID str instead
    project_type: str = ""

    language: str = ""
    tags: typing.List[str] = []
    readonly: bool = False
    source: str = ""
    copy_of: str = ""
    members: typing.List[User] = []
