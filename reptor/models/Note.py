from reptor.models.Base import BaseModel


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
