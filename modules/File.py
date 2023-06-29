import argparse

from classes.UploadBase import UploadBase
from utils.api import upload_files


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
        upload_files()


loader = File
