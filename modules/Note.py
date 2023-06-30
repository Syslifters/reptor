from classes.UploadBase import UploadBase
from api.NotesAPI import NotesAPI
from utils.conf import config


class Note(UploadBase):
    """
    upload as note
    """

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

    def run(self):
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

        NotesAPI().write_note(
            notename=notename,
            parent_notename=parent_notename,
            icon=icon,
            force_unlock=force_unlock,
            no_timestamp=no_timestamp
        )


loader = Note
