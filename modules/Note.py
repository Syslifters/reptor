from classes.UploadBase import UploadBase
from utils.api import write_note


class Note(UploadBase):
    """
    upload as note
    """


    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

    def run(self):
        write_note()


loader = Note
