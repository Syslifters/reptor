from core.modules.UploadBase import UploadBase
from api.NotesAPI import NotesAPI


class Note(UploadBase):
    """
    Author: Syslifters
    Website: https://github.com/Syslifters/reptor

    Short Help:
    Uploads a note
    """

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

    def run(self):
        notename = self.config.get_cli_overwrite().get("notename")
        parent_notename = None
        icon = None
        if notename:
            parent_notename = "Uploads"
        else:
            notename = "Uploads"
            icon = "📤"
        force_unlock = self.config.get_cli_overwrite().get("force_unlock")
        no_timestamp = self.config.get_cli_overwrite().get("no_timestamp")

        NotesAPI(self.reptor).write_note(
            notename=notename,
            parent_notename=parent_notename,
            icon=icon,
            force_unlock=force_unlock,  # type: ignore
            no_timestamp=no_timestamp,  # type: ignore
        )


loader = Note
