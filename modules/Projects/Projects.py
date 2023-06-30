from classes.Base import Base
from lib.api.clients import ProjectsApi

class Projects(Base):
    """
    Queries Server for Projects


    Sample commands:
        reptor projects
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)


    def run(self):
        projects_api : ProjectsApi = ProjectsApi()
        projects = projects_api.get_list()

        print(f"{'Project Name':<30}      ID")
        print(f"{'_':_<80}")
        for project in projects['results']:
            archived = ""
            if project['readonly']:
                archived = "(Archived)"

            print(f"{project['name']:<30}      {project['id']}      {archived}")
            print(f"{'_':_<80}")


loader = Projects