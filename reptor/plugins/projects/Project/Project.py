import json
from requests.exceptions import HTTPError
import typing


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
        self.search: typing.Optional[str] = kwargs.get("search")
        self.export: typing.Optional[str] = kwargs.get("export")
        self.render: bool = kwargs.get("render", False)
        self.upload: bool = kwargs.get("upload", False)
        self.duplicate: bool = kwargs.get("duplicate", False)
        self.output: typing.Optional[str] = kwargs.get("output")

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
        default_filename = self.reptor.api.projects.project.name or "project"
        if format == "archive":
            archive_content = self.reptor.api.projects.export()
            self._deliver_file(
                archive_content, filename, default_filename + ".tar.gz", upload
            )
            return

        project = self.reptor.api.projects.project.to_dict()
        output = ""
        if format == "json":
            output = json.dumps(project, indent=2)
        elif format == "toml":
            output = toml.dumps(project)
        elif format == "yaml":
            output = yaml.dump(project)
        else:
            raise ValueError(f"Unknown format: {format}")
        self._deliver_file(
            output.encode(), filename, f"{default_filename}.{format}", upload
        )

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

    def _render_project(self, filename=None, upload=False):
        # TODO: Documentation
        default_filename = (self.reptor.api.projects.project.name or "report") + ".pdf"
        try:
            pdf_content = self.reptor.api.projects.render()
        except HTTPError as e:
            try:
                for msg in e.response.json().get("messages", []):
                    if msg.get("level") == "error":
                        self.log.error(msg.get("message"))
                    elif msg.get("level") == "warning":
                        self.log.warning(msg.get("message"))
            except Exception:
                raise e
            return
        self._deliver_file(pdf_content, filename, default_filename, upload)

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