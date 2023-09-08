import json
import pathlib

import toml
import yaml

from reptor.lib.plugins.Base import Base
from reptor.utils.table import make_table


class Project(Base):
    """
    This plugin is used to interact with projects via the sysreptor API.
    """

    meta = {
        "name": "Project",
        "summary": "Work with projects",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = kwargs.get("search")
        self.export = kwargs.get("export")
        self.duplicate = kwargs.get("duplicate")
        self.output = kwargs.get("output")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        project_parser = parser.add_mutually_exclusive_group()
        parser.add_argument(
            "-o",
            "-output",
            "--output",
            metavar="FILENAME",
            help="Filename to store output, empty for stdout",
            action="store",
            default=None,
        )

        # Mutually exclusive options
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

    def _export_project(self, format="archive", filename=None):
        if format == "archive":
            self.reptor.api.projects.export(filename=filename)
            if filename:
                self.log.success(f"Exported to {filename}")
            return

        project = self.reptor.api.projects.project.to_dict()
        output = ""
        if format == "json":
            output = json.dumps(project, indent=2)
        elif format == "toml":
            output = toml.dumps(project)
        elif format == "yaml":
            output = yaml.dump(project)

        if not filename:
            self.console.print(output)
        else:
            with open(filename, "w") as f:
                f.write(output)
            self.log.success(f"Exported to {filename}")

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
            self._export_project(self.export, filename=self.output)
        elif self.duplicate:
            self._duplicate_project()
        else:
            self._search_project()


loader = Project
