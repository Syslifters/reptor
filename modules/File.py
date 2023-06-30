import argparse
import sys

from classes.UploadBase import UploadBase
from api.NotesAPI import NotesAPI
from utils.conf import config


class File(UploadBase):
    """
    upload as file
    """

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

        parser.add_argument("file", nargs="*",
                            type=argparse.FileType("r"),
                            help="files to upload; leave empty for stdin")
        parser.add_argument("-fn", "--filename",
                            help="filename if file provided via stdin")

    def run(self):
        files = config['cli'].get('file')
        if not files:
            files = [sys.stdin]
        filename = config['cli'].get('filename')
        notename = config['cli'].get('notename')
        parent_notename = None
        icon = None
        if notename:
            parent_notename = 'Uploads'
        else:
            notename = 'Uploads'
            icon = "📤"
        force_unlock = config['cli'].get('force_unlock')
        no_timestamp = config['cli'].get('no_timestamp')

        NotesAPI().upload_file(
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
