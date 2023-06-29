from classes.UploadBase import UploadBase
from utils.api import upload_files


class File(UploadBase):
    """
    upload as file
    """

    def run(self):
        upload_files()


loader = File
