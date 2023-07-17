from reptor.lib.plugins.Base import Base
from reptor.api.NotesAPI import NotesAPI

from reptor.lib.console import reptor_console
from reptor.utils.table import make_table


class Notes(Base):
    """ """

    meta = {
        "name": "Notes",
        "summary": "Lists current notes",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)

    def run(self):
        notes = self.reptor.api.notes.get_notes()

        table = make_table(["Title", "ID"])
        for note in notes:
            table.add_row(note.title, note.id)
        reptor_console.print(table)


loader = Notes
