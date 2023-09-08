import json
import tempfile
import typing
from contextlib import nullcontext
from io import DEFAULT_BUFFER_SIZE

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
        self.render = kwargs.get("render")
        self.upload = kwargs.get("upload")
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
        parser.add_argument(
            "-upload",
            "--upload",
            action="store_true",
            help="Used with --export or --render; uploads file to note",
            dest="upload",
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
            "-render",
            "--render",
            help="Render project",
            action="store_true",
            dest="render",
        )
        project_parser.add_argument(
            "-duplicate",
            "--duplicate",
            help="Duplicate project",
            action="store_true",
            dest="duplicate",
        )

    def _export_project(self, format="archive", filename=None, upload=False):
        if format == "archive":
            default_filename = (
                self.reptor.api.projects.project.name or "archive"
            ) + ".tar.gz"
            filename = self._get_filename(filename, default_filename, upload)

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
            self.print(output)
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

    def _get_filename(self, filename, default, upload) -> typing.Tuple[str, str]:
        if upload and (not filename or filename == "-"):
            return "tmp", ""
        if not filename:
            return "file", default
        if filename == "-":
            return "stdout", ""
        return "file", filename

    def _render_project(self, filename=None, upload=False):
        # TODO: implement as context manager - also for export
        # TODO: Address rendering errors
        # TODO: Documentation
        default_filename = (self.reptor.api.projects.project.name or "report") + ".pdf"
        filetype, filename = self._get_filename(filename, default_filename, upload)

        with tempfile.NamedTemporaryFile(
            buffering=DEFAULT_BUFFER_SIZE
        ) if filetype == "tmp" else nullcontext() as f:
            if f:
                filename = f.name
                self.reptor.api.projects.render(file=f)
            else:
                self.reptor.api.projects.render(filename=filename)
            if upload:
                if not f:
                    f = open(filename, "rb")
                f.seek(0)
                self.reptor.api.notes.upload_file([f], filename=default_filename)
                self.log.success(f"Uploaded to notes")
            elif filename:
                self.log.success(f"Exported to {filename}")

    def run(self):
        if self.export:
            self._export_project(self.export, filename=self.output, upload=self.upload)
        elif self.render:
            self._render_project(filename=self.output, upload=self.upload)
        elif self.duplicate:
            self._duplicate_project()
        else:
            self._search_project()


loader = Project
