import typing
from abc import abstractmethod

from reptor.api.models import Note  # Todo: Should be a Protocol!
from .base import BaseApiProtocol


class ApiNotesProtocol(BaseApiProtocol):
    project_id: str


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
