from dataclasses import dataclass
import datetime
import sys
import typing


@dataclass
class BaseModel:
    id: str = ""
    created: datetime.datetime = datetime.datetime.now()
    updated: datetime.datetime = datetime.datetime.now()

    def __init__(self, data: typing.Dict | None = None):
        if data:
            self._fill_from_api(data)

    def _fill_from_api(self, data: typing.Dict):
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


class FindingTemplate(BaseModel):
    details: str = ""
    lock_info: bool = False
    usage_count: int = 0
    source: str = ""
    tags: typing.List[str] = []
    language: str = ""
    status: str = ""
    data: FindingData | None = None

    custom_attributes: typing.List[dict] = []


class Note(BaseModel):
    lock_info: bool = False
    title: str = ""
    text: str = ""
    checked: bool = False
    icon_emoji: str = ""
    status_emoji: str = ""
    order: int = 0
    parent: str = ""


class ProjectType(BaseModel):
    source: str = ""
    scope: str = ""
    name: str = ""
    language: str = ""


class Project(BaseModel):
    name: str = ""

    # Todo: should be ProjectType but API returns no object, but ID str instead
    project_type: str = ""

    language: str = ""
    tags: typing.List[str] = []
    readonly: bool = False
    source: str = ""
    copy_of: str = ""
    members: typing.List[User] = []
