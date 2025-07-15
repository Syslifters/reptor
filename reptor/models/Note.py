import typing

from reptor.models.Base import BaseModel


class NoteBase(BaseModel):
    title: str = ""
    text: str = ""
    checked: typing.Optional[bool] = None
    icon_emoji: str = ""
    order: int = 0

    def __str__(self):
        return self.title
    
    def __repr__(self):
        return f'{self.__class__.__name__}(title="{self.title}", id="{self.id}")'


class Note(NoteBase):
    """
    This class represents a note in the Reptor system.

    Attributes:
        id (str): Note ID (uuid).
        created (datetime): Note creation time.
        updated (datetime): Note last update time.

        title (str): Note title.
        text (str): Note text content (markdown).
        checked (bool): Whether the note is checked (used for tasks).
        icon_emoji (str): Emoji icon for the note.
        order (int): Order of the note in the list.
        parent (str): ID of the parent note (if any).
    
    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    parent: str = ""

    @classmethod
    def from_note_template(cls, note_template: "NoteTemplate", **kwargs):
        note = cls(**kwargs)
        note.title = note_template.title
        note.text = note_template.text
        note.checked = note_template.checked
        note.icon_emoji = note_template.icon_emoji
        note.order = note_template.order
        if note_template.parent:
            note.parent = note_template.parent
        return note
    
    def __repr__(self):
        return f'Note(title="{self.title}", id="{self.id}", parent="{self.parent}")'


class NoteTemplate(NoteBase):
    template: str = ""
    template_data: dict = dict()
    parent: typing.Optional[str] = None  # parent preferred over parent_title
    parent_title: typing.Optional[str] = None
    children: typing.List["NoteTemplate"] = list()
    force_new: bool = False  # Create a new note even if same title exists

    def __init__(self, *args, **kwargs):
        self.children = list()
        self.template_data = dict()
        super().__init__(*args, **kwargs)

    @classmethod
    def from_kwargs(cls, **kwargs):
        return cls(data=kwargs)
    
    def __repr__(self):
        return f'NoteTemplate(title="{self.title}", id="{self.id}", parent="{self.parent}")'
