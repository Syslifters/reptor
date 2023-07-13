import pathlib

from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.lib.console import reptor_console
from reptor.lib.modules.Base import Base
from reptor.utils.table import make_table


class Translate(Base):
    """
    Author: Syslifters
    Website: https://github.com/Syslifters/reptor

    Short Help:
    Translate Projects and Templates to other languages
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects_api: ProjectsAPI = ProjectsAPI(self.reptor)
        self.from_lang = kwargs.get("from")
        self.to_lang = kwargs.get("to")


    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        project_parser = parser.add_mutually_exclusive_group()
        project_parser.add_argument(
            "-from", "--from",
            metavar="LANGUAGE_CODE",
            help="Language code of source language",
            action="store",
            default=None,
        )
        project_parser.add_argument(
            "-to", "--to",
            metavar="LANGUAGE_CODE",
            help="Language code of dest language",
            action="store",
            default=None,
        )

    def _translate_somthing(self):
        ...

    def run(self):
        pass

    # TODO in Projects können wir ja ohnehin --project-id angeben... --export id ist ambiguous
    


loader = Translate
