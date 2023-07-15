from reptor.lib.plugins.Base import Base
from reptor.api.NotesAPI import NotesAPI

from reptor.lib.console import reptor_console
from reptor.utils.table import make_table


class Notes(Base):
    """
    # Short Help:
    Queries Notes from reptor.api

    # Description:

    # Arguments:

    # Developer Notes:
    """

    def __init__(self, *kwargs):
        super().__init__(*kwargs)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)

    def run(self):
        notes_api: NotesAPI = NotesAPI(self.reptor)
        notes = notes_api.get_notes()

        table = make_table(["Title", "ID"])
        for note in notes:
            table.add_row(note.title, note.id)
        reptor_console.print(table)


loader = Notes
