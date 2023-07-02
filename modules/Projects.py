from classes.Base import Base
from api.ProjectsAPI import ProjectsAPI


class Projects(Base):
    """
    Queries Server for Projects


    Sample commands:
        reptor projects
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_search = kwargs.get("search")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        project_parser = parser.add_argument_group()
        project_parser.add_argument(
            "--search", help="Search for term", action="store", default=None
        )

    def run(self):
        projects_api: ProjectsAPI = ProjectsAPI()
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

            print(f"{project.name:<30}      {project.name}      {archived}")
            print(f"{'_':_<80}")


loader = Projects
