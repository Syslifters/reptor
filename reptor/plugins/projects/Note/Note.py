import json
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
        self.format = kwargs.get("format")
        self.notetitle = self.reptor.get_config().get_cli_overwrite().get("notetitle")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument("--list", help="list available notes", action="store_true")
        parser.add_argument(
            "--json",
            action="store_const",
            dest="format",
            const="json",
            default="plain",
        )

    def run(self):
        if self.list:
            self._list()
        else:
            self._write_note()

    def _list(self):
        notes = self.reptor.api.notes.get_notes()

        if self.format == "json":
            self.print(json.dumps([note.to_dict() for note in notes], indent=2))
        else:
            table = make_table(["Title", "ID"])
            for note in notes:
                table.add_row(note.title, note.id)
            self.console.print(table)

    def _write_note(self):
        parent_notetitle = None
        icon = None
        if self.notetitle:
            parent_notetitle = "Uploads"
        else:
            self.notetitle = "Uploads"
            icon = "📤"
        force_unlock = bool(
            self.reptor.get_config().get_cli_overwrite().get("force_unlock")
        )
        timestamp = not self.reptor.get_config().get_cli_overwrite().get("no_timestamp")

        """
        Notes accept stdin only
        Notes are added as child of 'Uploads' note
        If no notetitle defined, content gets appended to 'Uploads' note
        """
        self.info("Reading from stdin...")
        content = sys.stdin.read()

        self.reptor.api.notes.write_note(
            text=content,
            title=self.notetitle,
            parent_notetitle=parent_notetitle,
            icon=icon,
            force_unlock=force_unlock,
            timestamp=timestamp,
        )
        self.log.success("Successfully uploaded to notes.")


loader = Note
