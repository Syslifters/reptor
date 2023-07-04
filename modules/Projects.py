from core.modules.Base import Base
from api.ProjectsAPI import ProjectsAPI


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
            print("Exporting Project to current folder")
            projects_api.export(self.config.get_project_id())
            return

        if not self.arg_search:
            projects = projects_api.get_projects()
        else:
            projects = projects_api.search(self.arg_search)

        print(f"{'Project Name':<30}      ID")
        print(f"{'_':_<80}")
        for project in projects:
            archived = ""
            if project.readonly:
                archived = "(Archived)"

            print(f"{project.name:<30}      {project.id}      {archived}")
            print(f"{'_':_<80}")


loader = Projects
