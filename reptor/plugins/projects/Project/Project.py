import json
import typing
from contextlib import nullcontext

import tomli_w
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
        self.design: typing.Optional[str]
        self.design = kwargs.get("design") or getattr(self, "design", None)
        self.design = None if self.design == "-" else self.design
        self.upload: bool = kwargs.get("upload", False)
        self.duplicate: bool = kwargs.get("duplicate", False)
        self.output: typing.Optional[str] = kwargs.get("output")
        self.format: str = kwargs.get("format", "plain")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        project_parser = parser.add_mutually_exclusive_group()
        # Mutually exclusive options
        project_parser.add_argument(
            "--search",
            metavar="SEARCHTERM",
            help="Search for term",
            action="store",
            default=None,
        )
        project_parser.add_argument(
            "--export",
            help="Export project",
            choices=["tar.gz", "json", "toml", "yaml"],
            type=str.lower,
            action="store",
            dest="export",
            default=None,
        )
        project_parser.add_argument(
            "--render",
            help="Render project",
            action="store_true",
            dest="render",
        )
        project_parser.add_argument(
            "--duplicate",
            help="Duplicate project",
            action="store_true",
            dest="duplicate",
        )

        # Additional options
        parser.add_argument(
            "-o",
            "--output",
            metavar="FILENAME",
            help="Filename for output",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--design",
            metavar="DESIGN ID",
            help="Render project with alternative design",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--upload",
            action="store_true",
            help="Used with --export or --render; uploads file to note",
            dest="upload",
        )
        parser.add_argument(
            "--json",
            help="Used with --search; output as json",
            action="store_const",
            dest="format",
            const="json",
            default="plain",
        )

    def _export_project(self, format="tar.gz", filename=None, upload=False):
        stdout = False
        default_filename = self.reptor.api.projects.project.name or "project"

        if format == "tar.gz":
            if filename == "-":
                stdout = True
                filename = None
            archive_content = self.reptor.api.projects.export()
            self.deliver_file(
                content=archive_content,
                filename=filename or default_filename + ".tar.gz",
                upload=upload,
                stdout=stdout,
            )
            return

        if filename == "-" or filename is None:
            stdout = True
            filename = None
        project = self.reptor.api.projects.project.to_dict()
        output = ""
        if format == "json":
            output = json.dumps(project, indent=2)
        elif format == "toml":
            output = tomli_w.dumps(project)
        elif format == "yaml":
            output = yaml.dump(project)
        else:
            raise ValueError(f"Unknown format: {format}")
        self.deliver_file(
            content=output.encode(),
            filename=filename or f"{default_filename}.{format}",
            upload=upload,
            stdout=stdout,
        )

    def _search_project(self):
        if self.search is not None:
            projects = self.reptor.api.projects.search(self.search)
        else:
            projects = self.reptor.api.projects.get_projects()

        if self.format == "json":
            self.print(
                json.dumps([project.to_dict() for project in projects], indent=2)
            )
        else:
            table = make_table(["Title", "ID", "Archived"])
            for project in projects:
                archived = ""
                if project.readonly:
                    archived = "[red]Yes[/red]"
                table.add_row(project.name, project.id, archived)

            self.console.print(table)

    def _duplicate_project(self):
        duplicated_project = self.reptor.api.projects.duplicate_project()
        project_title = duplicated_project.name
        project_id = duplicated_project.id
        self.success(f"Duplicated to '{project_title}' ({project_id})")

    def _render_project(self, filename=None, upload=False):
        stdout = False
        default_filename = (self.reptor.api.projects.project.name or "report") + ".pdf"
        if filename == "-":
            stdout = True
            filename = None
        with self.reptor.api.projects.duplicate_and_cleanup() if self.design else nullcontext():
            # Update design
            if self.design:
                self.reptor.api.projects.update_project_design(self.design, force=True)
            pdf_content = self.reptor.api.projects.render()
        self.deliver_file(
            content=pdf_content,
            filename=filename or default_filename,
            upload=upload,
            stdout=stdout,
        )

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
