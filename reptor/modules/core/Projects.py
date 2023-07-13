import pathlib

from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.lib.console import reptor_console
from reptor.lib.modules.Base import Base
from reptor.utils.table import make_table


class Projects(Base):
    """
    Author: Syslifters
    Website: https://github.com/Syslifters/reptor

    Short Help:
    Queries Projects from reptor.api
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects_api: ProjectsAPI = ProjectsAPI(self.reptor)
        self.search = kwargs.get("search")
        self.export = kwargs.get("export")
        self.duplicate = kwargs.get("duplicate")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        project_parser = parser.add_mutually_exclusive_group()
        project_parser.add_argument(
            "-search", "--search",
            metavar="SEARCHTERM",
            help="Search for term",
            action="store",
            default=None,
        )
        project_parser.add_argument(
            "-export", "--export",
            help="Export project to tar.gz file",
            action="store_true",
            dest='export',
        )
        project_parser.add_argument(
            "-duplicate", "--duplicate",
            help="Duplicate project",
            action="store_true",
            dest='duplicate',
        )

    def _export_project(self):
        filepath = pathlib.Path().cwd()
        file_name = filepath / f"{self.projects_api.project_id}.tar.gz"
        self.projects_api.export(file_name=file_name)
        self.reptor.logger.success(f"Written to: {file_name}")

    def _search_project(self):
        if self.search is not None:
            projects = self.projects_api.search(self.search)
        else:
            projects = self.projects_api.get_projects()

        table = make_table(["Title", "ID", "Archived"])

        for project in projects:
            archived = ""
            if project.readonly:
                archived = "[red]Yes[/red]"
            table.add_row(project.name, project.id, archived)

        reptor_console.print(table)

    def _duplicate_project(self):
        new_project = self.projects_api.duplicate()
        project_title = new_project['name']
        project_id = new_project['id']
        self.reptor.logger.success(
            f"Duplicated to '{project_title}' ({project_id})")

    def run(self):
        if self.export:
            self._export_project()
        elif self.duplicate:
            self._duplicate_project()
        else:
            self._search_project()


loader = Projects
