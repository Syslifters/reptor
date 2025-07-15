from reptor.models.Base import BaseModel


import typing


class User(BaseModel):
    """
    Representation of a SysReptor user.

    Attributes:
        id (str): User ID (uuid).
        created (datetime): Date when the user was created.
        updated (datetime): Date when the user was last updated.
        
        username (str): Username.
        is_active (bool): Whether the user account is active.
        name (str): Display name of the user (computed propery; consists of title and name fields).
        
        title_before (str): Academic title before the name.
        first_name (str): User's first name.
        middle_name (str): User's middle name.
        last_name (str): User's last name.
        title_after (str): Academic title after the name.

        color (str): Color associated with the user (for UI purposes).
        email (str): User's email address.
        phone (str): User's phone number.
        mobile (str): User's mobile phone number.
        
        scope (List[str]): List of scopes/permissions for the user (e.g., `template_editor`, `designer`, `user_manager`).
        is_superuser (bool): Whether the user has superuser privileges.
        is_designer (bool): Whether the user can design project templates.
        is_template_editor (bool): Whether the user can edit templates.
        is_guest (bool): Whether the user is a guest user.
        is_user_manager (bool): Whether the user can manage other users.
        is_system_user (bool): Whether this is a system user account.
        is_global_archiver (bool): Whether the user can archive projects globally.
        is_mfa_enabled (bool): Whether multi-factor authentication is enabled.
        can_login_local (bool): Whether the user can login using local authentication.
        can_login_sso (bool): Whether the user can login using SSO.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """

    username: str = ""
    name: str = ""
    color: str = ""
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

    def __str__(self):
        return f"{self.name} ({self.username})"

    def __repr__(self):
        return f'User(username="{self.username}", name="{self.name}", email="{self.email}", id="{self.id}")'