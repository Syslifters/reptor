
from .NotesAPI import NotesAPI
from .ProjectDesignsAPI import ProjectDesignsAPI
from .ProjectsAPI import ProjectsAPI
from .TemplatesAPI import TemplatesAPI


class APIManager:
    _notes: NotesAPI = None
    _projects: ProjectsAPI = None
    _project_designs: ProjectDesignsAPI = None
    _templates: TemplatesAPI = None

    def __init__(self, **kwargs) -> None:
        self._reptor = kwargs["reptor"]
        self._project_id = self._reptor.get_active_project_id()

    @property
    def notes(self) -> NotesAPI:
        if not self._notes:
            self._notes = NotesAPI(reptor=self._reptor, project_id=self._project_id)
        return self._notes

    @property
    def projects(self) -> ProjectsAPI:
        if not self._projects:
            self._projects = ProjectsAPI(
                reptor=self._reptor, project_id=self._project_id
            )
        return self._projects

    def switch_project(self, new_project_id) -> None:
        self._project_id = new_project_id
        self._projects = None
        self._notes = None
        self._project_designs = None
        self._templates = None

    @property
    def project_designs(self) -> ProjectDesignsAPI:
        if not self._project_designs:
            project_design_id = self.projects.project.project_type
            self._project_designs = ProjectDesignsAPI(
                reptor=self._reptor, project_design_id=project_design_id
            )
        return self._project_designs

    @property
    def templates(self) -> TemplatesAPI:
        if not self._templates:
            self._templates = TemplatesAPI(
                reptor=self._reptor, project_id=self._project_id
            )
        return self._templates
