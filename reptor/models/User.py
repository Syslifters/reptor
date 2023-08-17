from reptor.models.Base import BaseModel


import typing


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
