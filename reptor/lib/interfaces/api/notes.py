import typing
from abc import abstractmethod

from reptor.api.models import Note


class ApiNotesProtocol(typing.Protocol):
    @abstractmethod
    def get_notes() -> typing.List[Note]:
        ...

    @abstractmethod
    def create_note():
        ...

    @abstractmethod
    def set_icon():
        ...

    @abstractmethod
    def write_note():
        ...

    @abstractmethod
    def get_note_by_title():
        ...

    @abstractmethod
    def upload_file():
        ...
