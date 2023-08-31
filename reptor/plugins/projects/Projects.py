import pathlib
import json
import toml
import yaml

from reptor.lib.plugins.Base import Base
from reptor.utils.table import make_table


class Projects(Base):
    """
    This plugin is used to interact with the projects via the sysreptor API.
    """

    meta = {
        "name": "Projects",
        "summary": "Queries Projects from reptor.api",
    }

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
            help="Export project",
            choices=["archive", "json", "toml", "yaml"],
            type=str.lower,
            action="store",
            dest="export",
            default=None,
        )
        project_parser.add_argument(
            "-duplicate",
            "--duplicate",
            help="Duplicate project",
            action="store_true",
            dest="duplicate",
        )

    def _export_project(self, format="archive"):
        if format == "archive":
            filepath = pathlib.Path().cwd()
            file_name = filepath / f"{self.reptor.api.projects.project_id}.tar.gz"
            self.reptor.api.projects.export(file_name=file_name)
            return

        # Get Project
        project = self.reptor.api.projects.project.to_dict()
        if format == "json":
            self.console.print(json.dumps(project, indent=2))
        elif format == "toml":
            self.console.print(toml.dumps(project))
        elif format == "yaml":
            self.console.print(yaml.dump(project))

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

        self.console.print(table)

    def _duplicate_project(self):
        duplicated_project = self.reptor.api.projects.duplicate()
        project_title = duplicated_project.name
        project_id = duplicated_project.id
        self.success(f"Duplicated to '{project_title}' ({project_id})")

    def run(self):
        if self.export:
            self._export_project(self.export)
        elif self.duplicate:
            self._duplicate_project()
        else:
            self._search_project()


loader = Projects
