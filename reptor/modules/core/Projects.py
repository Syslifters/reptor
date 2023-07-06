from reptor.lib.modules.Base import Base
from reptor.api.ProjectsAPI import ProjectsAPI

from reptor.lib.console import reptor_console

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
        self.arg_search = kwargs.get("search")
        self.arg_export = kwargs.get("export")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        project_parser = parser.add_argument_group()
        project_parser.add_argument(
            "--search", help="Search for term", action="store", default=None
        )
        project_parser.add_argument(
            "--export",
            help="Export Project to tar.gz file",
            action="store_true",
            default=None,
        )

    def run(self):
        projects_api: ProjectsAPI = ProjectsAPI(self.reptor)

        if self.arg_export:
            self.reptor.logger.success("Exporting Project to current folder")
            projects_api.export(self.config.get_project_id())
            return

        if not self.arg_search:
            projects = projects_api.get_projects()
        else:
            projects = projects_api.search(self.arg_search)

        table = make_table(["Title", "ID", "Archived"])

        for project in projects:
            archived = ""
            if project.readonly:
                archived = "[red]Yes[/red]"

            table.add_row(project.name, project.id, archived)

        reptor_console.print(table)


loader = Projects
