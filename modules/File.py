import argparse
import sys

from core.modules.UploadBase import UploadBase
from api.NotesAPI import NotesAPI


class File(UploadBase):
    """
    Author: Syslifters
    Website: https://github.com/Syslifters/reptor

    Short Help:
    Uploads a file
    """

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

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
        files = self.config.get("cli").get("file")
        if not files:
            files = [sys.stdin]
        filename = self.config.get("cli").get("filename")
        notename = self.config.get("cli").get("notename")
        parent_notename = None
        icon = None
        if notename:
            parent_notename = "Uploads"
        else:
            notename = "Uploads"
            icon = "📤"
        force_unlock = self.config.get("cli").get("force_unlock")
        no_timestamp = self.config.get("cli").get("no_timestamp")

        NotesAPI(self.reptor).upload_file(
            files=files,
            filename=filename,
            caption=filename,
            notename=notename,
            parent_notename=parent_notename,
            no_timestamp=no_timestamp,
            force_unlock=force_unlock,
            icon=icon,
        )


loader = File
