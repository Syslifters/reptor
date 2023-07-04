from rich import box
from rich.table import Table

from core.modules.Base import Base
from api.ProjectsAPI import ProjectsAPI

from core.console import reptor_console
from core.logger import reptor_logger


class Projects(Base):
    """
    Queries Server for Projects


    Sample commands:
        reptor projects
    """

    def __init__(self, reptor, **kwargs):
        super().__init__(reptor, **kwargs)
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
            reptor_logger.success("Exporting Project to current folder")
            projects_api.export(self.config.get_project_id())
            return

        if not self.arg_search:
            projects = projects_api.get_projects()
        else:
            projects = projects_api.search(self.arg_search)

        table = Table(show_header=True, header_style="bold yellow")
        table.caption = "Your Projects"
        table.row_styles = ["none", "dim"]
        table.border_style = "bright_yellow"
        table.box = box.SQUARE
        table.pad_edge = False
        table.add_column("Title")
        table.add_column("ID")
        table.add_column("Archived", justify="right")

        for project in projects:
            archived = ""
            if project.readonly:
                archived = "[red]Yes[/red]"

            table.add_row(project.name, project.id, archived)

        reptor_console.print(table)


loader = Projects
