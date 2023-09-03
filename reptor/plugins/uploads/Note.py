import sys

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.utils.table import make_table


class Note(UploadBase):
    """ """

    meta = {
        "name": "Note",
        "summary": "Uploads and lists notes",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list = kwargs.get("list")
        self.notename = self.reptor.get_config().get_cli_overwrite().get("notename")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        parser.add_argument("--list", help="list available notes", action="store_true")

    def run(self):
        if self.list:
            self._list()
        else:
            self._write_note()

    def _list(self):
        notes = self.reptor.api.notes.get_notes()

        table = make_table(["Title", "ID"])
        for note in notes:
            table.add_row(note.title, note.id)
        self.console.print(table)

    def _write_note(self):
        parent_notename = None
        icon = None
        if self.notename:
            parent_notename = "Uploads"
        else:
            self.notename = "Uploads"
            icon = "📤"
        force_unlock = self.reptor.get_config().get_cli_overwrite().get("force_unlock")
        no_timestamp = self.reptor.get_config().get_cli_overwrite().get("no_timestamp")

        """
        Notes accept stdin only
        Notes are added as child of 'Uploads' note
        If no notename defined, content gets appended to 'Uploads' note
        """
        self.info("Reading from stdin...")
        content = sys.stdin.read()

        self.reptor.api.notes.write_note(
            content=content,
            notename=self.notename,
            parent_notename=parent_notename,
            icon=icon,
            force_unlock=force_unlock,  # type: ignore
            no_timestamp=no_timestamp,  # type: ignore
        )
        self.log.success("Successfully uploaded to notes.")


loader = Note
