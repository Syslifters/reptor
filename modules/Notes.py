from core.modules.Base import Base
from api.NotesAPI import NotesAPI


class Notes(Base):
    """
    Queries Server for Notes


    Sample commands:
        reptor notes
    """

    def __init__(self, reptor, **kwargs):
        super().__init__(reptor, **kwargs)

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)

    def run(self):
        notes_api: NotesAPI = NotesAPI(self.reptor)
        notes = notes_api.get_notes()

        print(f"{'Title':<30} ID")
        print(f"{'_':_<80}")
        for note in notes:
            print(f"{note['title']:<30} {note['id']}")
            print(f"{'_':_<80}")


loader = Notes
