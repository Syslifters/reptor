from classes.UploadBase import UploadBase
from utils.api import write_note


class Note(UploadBase):
    """
    upload as note
    """

    def run(self):
        write_note()


loader = Note
