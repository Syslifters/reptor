import typing

from reptor.models.Base import BaseModel


class NoteBase(BaseModel):
    lock_info: bool = False
    title: str = ""
    text: str = ""
    checked: typing.Optional[bool] = None
    icon_emoji: str = ""
    status_emoji: str = ""
    order: int = 0


class Note(NoteBase):
    parent: str = ""

    @classmethod
    def from_note_template(cls, note_template: "NoteTemplate", **kwargs):
        note = cls(**kwargs)
        note.title = note_template.title
        note.text = note_template.text
        note.checked = note_template.checked
        note.icon_emoji = note_template.icon_emoji
        note.status_emoji = note_template.status_emoji
        note.order = note_template.order
        if note_template.parent:
            note.parent = note_template.parent
        return note


class NoteTemplate(NoteBase):
    template: str = ""
    template_data: dict = dict()
    parent: typing.Optional[str] = None  # Parent ID preferred over parent_notetitle
    parent_notetitle: typing.Optional[str] = None
    children: typing.List["NoteTemplate"] = list()

    def __init__(self, *args, **kwargs):
        self.children = list()
        self.template_data = dict()
        super().__init__(*args, **kwargs)

    @classmethod
    def from_kwargs(cls, **kwargs):
        return cls(data=kwargs)
