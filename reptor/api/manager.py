from reptor.lib.interfaces.apimanager import APIManagerProtocol

from .NotesAPI import NotesAPI
from .ProjectsAPI import ProjectsAPI
from .TemplatesAPI import TemplatesAPI


class APIManager(APIManagerProtocol):
    _notes: NotesAPI = None
    _projects: ProjectsAPI = None
    _templates: TemplatesAPI = None

    def __init__(self, **kwargs) -> None:
        self._reptor = kwargs.get("reptor")

    @property
    def notes(self) -> NotesAPI:
        if not self._notes:
            self._notes = NotesAPI(reptor=self._reptor)
        return self._notes

    @property
    def projects(self) -> ProjectsAPI:
        if not self._projects:
            self._projects = ProjectsAPI(reptor=self._reptor)
        return self._projects

    @property
    def templates(self) -> TemplatesAPI:
        if not self._templates:
            self._templates = TemplatesAPI(reptor=self._reptor)
        return self._templates
