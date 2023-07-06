from core.modules.Base import Base
from api.NotesAPI import NotesAPI

from core.console import reptor_console
from utils.table import make_table


class Notes(Base):
    """
    Author: Syslifters
    Website: https://github.com/Syslifters/reptor

    Short Help:
    Queries Notes from API
    """

    def __init__(self, *kwargs):
        super().__init__(*kwargs)

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

    def run(self):
        notes_api: NotesAPI = NotesAPI(self.reptor)
        notes = notes_api.get_notes()

        table = make_table(["Title", "ID"])
        for note in notes:
            table.add_row(note.title, note.id)
        reptor_console.print(table)


loader = Notes
