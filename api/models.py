from dataclasses import dataclass
import datetime
import sys
import typing


@dataclass
class BaseModel:
    id: str = None
    created: datetime.datetime = None
    updated: datetime.datetime = None

    def __init__(self, data: str = None):
        if data:
            self._fill_from_api(data)

    def _fill_from_api(self, data: str):
        """Fills Model from API return JSON data

        Args:
            data (str): API Return Data
        """
        basemodel_class_type_hints = typing.get_type_hints(BaseModel)
        current_class_type_hints = typing.get_type_hints(self)
        combined_class_type_hints = {
            **basemodel_class_type_hints,
            **current_class_type_hints,
        }

        for attr in combined_class_type_hints.items():
            if attr[0] in data:
                # Check if one of our models, then proceed recursively
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
                ]:
                    cls = getattr(sys.modules[__name__], model_class)

                    if is_list:
                        item_list = list()
                        for item in data[attr[0]]:
                            item_list.append(cls(item))
                        self.__setattr__(attr[0], item_list)
                    else:
                        self.__setattr__(attr[0], cls(data[attr[0]]))
                else:
                    # Fill each attribute
                    self.__setattr__(attr[0], data[attr[0]])

    def _to_api_json(self):
        ...


class User(BaseModel):
    username: str = None
    name: str = None
    title_before: str = None
    first_name: str = None
    middle_name: str = None
    last_name: str = None
    title_after: str = None
    is_active: bool = False
    roles: typing.List[str] = []
    email: str = None
    phone: str = None
    mobile: str = None
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
    title: str = None
    cvss: str = None
    summary: str = None
    description: str = None
    precondition: str = None
    impact: str = None
    recommendation: str = None
    short_recommendation: str = None
    references: typing.List[str] = []
    affected_components: typing.List[str] = []
    owasp_top10_2021: str = None
    wstg_category: str = None
    retest_notes: str = None
    retest_status: str = None
    evidence: str = None


class FindingTemplate(BaseModel):
    details: str = None
    lock_info: bool = False
    usage_count: int = None
    source: str = None
    tags: typing.List[str] = []
    language: str = None
    status: str = None
    data: FindingData = None

    custom_attributes: typing.List[dict] = []


class Note(BaseModel):
    lock_info: bool = False
    title: str = None
    text: str = None
    checked: bool = False
    icon_emoji: str = None
    status_emoji: str = None
    order: int = None
    parent: str = None


class ProjectType(BaseModel):
    source: str = None
    scope: str = None
    name: str = None
    language: str = None


class Project(BaseModel):
    name: str = None
    project_type: str = None  # Todo: should be ProjectType but API returns no object, but ID str instead
    language: str = None
    tags: typing.List[str] = []
    readonly: bool = False
    source: str = None
    copy_of: str = None
    members: typing.List[User] = []
