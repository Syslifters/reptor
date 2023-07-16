import pathlib

from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.lib.console import reptor_console
from reptor.lib.plugins.Base import Base
from reptor.utils.table import make_table


class Projects(Base):
    """
    # Short Help:
    Queries Projects from reptor.api

    # Description:

    # Arguments:

    # Developer Notes:
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = kwargs.get("search")
        self.export = kwargs.get("export")
        self.duplicate = kwargs.get("duplicate")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        project_parser = parser.add_mutually_exclusive_group()
        project_parser.add_argument(
            "-search",
            "--search",
            metavar="SEARCHTERM",
            help="Search for term",
            action="store",
            default=None,
        )
        project_parser.add_argument(
            "-export",
            "--export",
            help="Export project to tar.gz file",
            action="store_true",
            dest="export",
        )
        project_parser.add_argument(
            "-duplicate",
            "--duplicate",
            help="Duplicate project",
            action="store_true",
            dest="duplicate",
        )

    def _export_project(self):
        filepath = pathlib.Path().cwd()
        file_name = filepath / f"{self.reptor.api.projects.project_id}.tar.gz"
        self.reptor.api.projects.export(file_name=file_name)
        self.reptor.logger.success(f"Written to: {file_name}")

    def _search_project(self):
        if self.search is not None:
            projects = self.reptor.api.projects.search(self.search)
        else:
            projects = self.reptor.api.projects.get_projects()

        table = make_table(["Title", "ID", "Archived"])

        for project in projects:
            archived = ""
            if project.readonly:
                archived = "[red]Yes[/red]"
            table.add_row(project.name, project.id, archived)

        reptor_console.print(table)

    def _duplicate_project(self):
        duplicated_project = self.reptor.api.projects.duplicate()
        project_title = duplicated_project.name
        project_id = duplicated_project.id
        self.reptor.logger.success(f"Duplicated to '{project_title}' ({project_id})")

    def run(self):
        if self.export:
            self._export_project()
        elif self.duplicate:
            self._duplicate_project()
        else:
            self._search_project()


loader = Projects
