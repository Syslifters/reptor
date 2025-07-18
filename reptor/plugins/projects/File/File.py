import argparse
import sys

from reptor.lib.plugins.UploadBase import UploadBase


class File(UploadBase):
    """
    Arguments:
    * --file        files to upload; leave empty for stdin
    * --filename|-fn    filename if file provided via stdin

    """

    meta = {
        "name": "File",
        "summary": "Uploads a file",
    }

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)

        parser.add_argument(
            "file",
            nargs="*",
            type=argparse.FileType("r"),
            help="files to upload; leave empty for stdin",
        )
        parser.add_argument(
            "-fn", "--filename", help="filename if file provided via stdin"
        )

    def run(self):
        files = self.reptor.get_config().get("cli").get("file")
        if not files:
            files = [sys.stdin]
        filename = self.reptor.get_config().get("cli").get("filename")
        notetitle = self.reptor.get_config().get("cli").get("notetitle")
        parent_notetitle = None
        icon = None
        if notetitle:
            parent_notetitle = "Uploads"
        else:
            notetitle = "Uploads"
            icon = "📤"
        timestamp = not self.reptor.get_config().get("cli", dict()).get("no_timestamp")

        for file in files:
            self.reptor.api.notes.upload_file(
                file=file,
                filename=filename,
                caption=filename,
                note_title=notetitle,
                parent_title=parent_notetitle,
                timestamp=timestamp,
                icon=icon,
            )


loader = File
