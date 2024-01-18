import glob
import json
import logging
import os
import sys
import typing
from pathlib import Path
from xml.etree import ElementTree

import tomli
import xmltodict
from django.template import Context, Template
from django.template.loader import render_to_string

import reptor.settings as settings
from reptor.models.Finding import Finding
from reptor.models.Note import NoteTemplate
from reptor.models.ProjectDesign import ProjectDesign

from .Base import Base

log = logging.getLogger("reptor")


class ToolBase(Base):
    """The ToolBase provides plugin developers with all functionality that
    is commonly encountered when writing a plugin.


    Attributes:
        raw_input: Unformatted input, either from stdin or a file
        template: The .md file to be used during formatting
    """

    FINDING_PREFIX = "finding_"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = kwargs.get("action")
        self.notetitle = self.notetitle or self.__class__.__name__.lower()
        self.push_findings = kwargs.get("push_findings")
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None
        self.note_templates = None
        self.findings = []
        self.timestamp = (
            not self.reptor.get_config().get("cli", dict()).get("no_timestamp")
        )
        self.force_unlock = (
            self.reptor.get_config().get("cli", dict()).get("force_unlock")
        )

        self.input_format = kwargs.get("format")
        self.template = kwargs.get("template", self.template)

        if self.template_paths:
            settings.TEMPLATES[0]["DIRS"] = self.template_paths

    @classmethod
    def get_plugin_dir_paths(
        cls,
        plugin_path: Path,
        dirname: str,
        skip_user_plugins: bool = False,
    ) -> typing.List[Path]:
        if plugin_path is None:
            raise ValueError("plugin_path must not be None")
        dir_paths = list()
        if skip_user_plugins:
            user_plugin_path = None
        else:
            user_plugin_path = settings.PLUGIN_DIRS_USER / os.path.basename(plugin_path)

        for path in [
            user_plugin_path,
            plugin_path,
        ]:  # Keep order: files from user directory override
            if path is None:
                continue
            dir_path = Path(os.path.normpath(Path(path) / dirname))

            if dir_path not in dir_paths and os.path.isdir(dir_path):
                dir_paths.append(dir_path)

        # Return list of existing template paths
        return dir_paths

    @classmethod
    def get_filenames_from_paths(cls, dir_paths: list, filetype: str):
        """
        takes a list of paths and returns a list of filenames without file extension
        """
        filetype = f"*.{filetype.strip('.')}"
        # Get template names from paths
        files_from_plugin_dir = list()
        for path in dir_paths:
            files = [
                os.path.basename(f).rsplit(".", 1)[0]
                for f in glob.glob(os.path.join(path, filetype))
            ]
            files_from_plugin_dir.extend(
                [t for t in files if t not in files_from_plugin_dir]
            )
        return sorted(files_from_plugin_dir)

    @classmethod
    def setup_class(cls, plugin_path: Path, skip_user_plugins: bool = False):
        # Get template and finding paths from plugin and userdir
        cls.finding_paths = cls.get_plugin_dir_paths(
            plugin_path,
            settings.FINDING_TEMPLATES_DIR_NAME,
            skip_user_plugins=skip_user_plugins,
        )
        cls.template_paths = cls.get_plugin_dir_paths(
            plugin_path,
            settings.PLUGIN_TEMPLATES_DIR_NAME,
            skip_user_plugins=skip_user_plugins,
        )
        cls.templates = cls.get_filenames_from_paths(cls.template_paths, "md")

        # Choose default template
        if cls.templates:
            if len(cls.templates) == 1:
                cls.template = cls.templates[0]
            elif len(cls.templates) > 1:
                default_templates = [t for t in cls.templates if "default" in t]
                try:
                    cls.template = default_templates[0]
                except IndexError:
                    cls.template = cls.templates[0]

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        if plugin_filepath:
            cls.setup_class(Path(os.path.dirname(plugin_filepath)))

        action_group = parser.add_mutually_exclusive_group()
        action_group.title = "action_group"
        action_group.add_argument(
            "--parse",
            action="store_const",
            dest="action",
            const="parse",
            default="format",
        )
        if cls.templates:
            action_group.add_argument(
                "--format",
                action="store_const",
                dest="action",
                const="format",
                default="format",
            )
            action_group.add_argument(
                "--upload",
                action="store_const",
                dest="action",
                const="upload",
                default="format",
            )

        if cls._get_finding_methods():
            action_group.add_argument(
                "--push-findings",
                action="store_true",
            )

        if any(
            [
                cls.parse_xml != ToolBase.parse_xml,
                cls.parse_json != ToolBase.parse_json,
                cls.parse_csv != ToolBase.parse_csv,
            ]
        ):  # Prevent adding input_format_group if no parsing methods are implemented
            input_format_group = parser.add_mutually_exclusive_group()
            input_format_group.title = "input_format_group"

            # Add parsing options only if implemented by modules
            if cls.parse_xml != ToolBase.parse_xml:
                input_format_group.add_argument(
                    "--xml",
                    action="store_const",
                    dest="format",
                    const="xml",
                    default="raw",
                )
            if cls.parse_json != ToolBase.parse_json:
                input_format_group.add_argument(
                    "--json",
                    action="store_const",
                    dest="format",
                    const="json",
                    default="raw",
                )
            if cls.parse_csv != ToolBase.parse_csv:
                input_format_group.add_argument(
                    "--csv",
                    action="store_const",
                    dest="format",
                    const="csv",
                    default="raw",
                )

    @classmethod
    def get_input_format_group(cls, parser):
        # Find input_format_group
        for group in parser._mutually_exclusive_groups:
            if group.title == "input_format_group":
                return group
        else:
            raise ValueError("input_format_group not found")

    @classmethod
    def _get_finding_methods(cls) -> typing.List[typing.Callable]:
        finding_method_names = [
            func
            for func in dir(cls)
            if callable(getattr(cls, func)) and func.startswith(cls.FINDING_PREFIX)
        ]
        return [getattr(cls, n) for n in finding_method_names]

    def run(self):
        """
        The run method is always called by the main reptor application.

        The flow is:

        Parsing -> Formatting -> Uploading
        """
        if self.push_findings:
            self.generate_and_push_findings()
            if self.action == "upload":
                # Also upload to notes
                self.upload()
            return

        if self.action == "parse":
            self.parse()
            self.print(self.parsed_input)
        elif self.action == "format":
            self.format()
            self.print(self.formatted_input)
        elif self.action == "upload":
            self.upload()

    def load(self):
        """Puts the stdin into raw_input"""
        self.raw_input = sys.stdin.read()

    def parse_xml(self, as_dict=True):
        if as_dict:
            self.parsed_input = xmltodict.parse(self.raw_input)  # type: ignore
        else:
            if not self.file_path and self.raw_input:
                self.xml_root = ElementTree.fromstring(self.raw_input)
            else:
                self.xml_root = ElementTree.parse(self.file_path).getroot()

    def parse_json(self):
        self.parsed_input = json.loads(self.raw_input)  # type: ignore

    def parse_csv(self):
        raise NotImplementedError("Parse csv data is not implemented for this plugin.")

    def parse_raw(self):
        raise NotImplementedError("Parse raw data is not implemented for this plugin.")

    def parse(self):
        """
        Directs the input to the correct sub parsing method. For every toolbase
        plugin it is possible to handle --xml, --csv, --json or raw input.

        Depending on the arguments the corresponding sub parser method is called.

        If you decide not to support one of these, it won't be possible to provide
        the corresponding argument.
        """
        if not self.raw_input and not self.file_path:
            self.load()

        if self.input_format == "xml":
            self.parse_xml()
        elif self.input_format == "json":
            self.parse_json()
        elif self.input_format == "csv":
            self.parse_csv()

    def format(self):
        """Checks if `self.parsed_input` is set.
        If not it starts the parsing process.

        Once there is parsed data it is run through the Django Templating Engine.

        The template is set via `self.template`.
        """
        if not self.parsed_input:
            self.parse()

        if data := self.create_notes():
            if isinstance(data, NoteTemplate):
                data = [data]
            self.note_templates = data
            self.formatted_input = self.format_note_template(data)
            return
        elif data := self.preprocess_for_template():
            self.formatted_input = render_to_string(f"{self.template}.md", data)
            return

        raise ValueError(
            "Cannot format data. Did not get data from preprocess_for_template() and create_notes()."
        )

    def format_note_template(self, note_templates: typing.List[NoteTemplate], level=1):
        formatted_input = ""
        for note_template in note_templates:
            if note_template.template:
                note_template.text = render_to_string(
                    f"{note_template.template}.md", note_template.template_data
                )
            if note_template.title:
                formatted_input += f"{'#' * level} {note_template.title}\n\n"
            if note_template.text:
                formatted_input += f"{note_template.text}\n\n"

            formatted_input += self.format_note_template(
                note_template.children, level=level + 1
            )
        return formatted_input

    def preprocess_for_template(self) -> dict:
        return {"data": self.parsed_input}

    def create_notes(
        self,
    ) -> typing.Union[NoteTemplate, typing.List[NoteTemplate], None]:
        pass

    def upload(self):
        """Uploads the `self.formatted_input` to sysreptor via the NotesAPI."""
        if not self.formatted_input:
            self.format()

        if self.note_templates:
            self.reptor.api.notes.write_note_templates(
                self.note_templates,
                timestamp=self.timestamp,
                force_unlock=self.force_unlock,
            )
        else:
            parent_notetitle = "Uploads" if self.notetitle != "Uploads" else None
            self.reptor.api.notes.write_note(
                title=self.notetitle,
                text=self.formatted_input,
                parent_notetitle=parent_notetitle,
                icon_emoji=self.note_icon,
                timestamp=self.timestamp,
                force_unlock=self.force_unlock,
            )
        self.log.success("Successfully uploaded to notes.")

    def generate_and_push_findings(self) -> None:
        self.generate_findings()
        if len(self.findings) == 0:
            self.log.display("No findings generated.")
            return
        project_findings = [
            Finding(f, self.reptor.api.project_designs.project_design)
            for f in self.reptor.api.projects.get_findings()
        ]
        project_finding_titles = [f.data.title.value for f in project_findings]
        project_findings_from_templates = [f.template for f in project_findings]
        for finding in self.findings:
            self.log.info(f'Checking if finding "{finding.data.title.value}" exists')
            if finding.template:
                if finding.template in project_findings_from_templates:
                    self.log.display(
                        f'Finding "{finding.data.title.value}" already created from template. Skipping.'
                    )
                    continue
            elif finding.data.title.value in project_finding_titles:
                self.log.display(
                    f'Finding "{finding.data.title.value}" already exists. Skipping.'
                )
                continue

            self.log.info(f'Pushing finding "{finding.data.title.value}"')
            if finding.template:
                # First create from template to keep template reference
                created_finding = self.reptor.api.projects.create_finding_from_template(
                    finding.template
                )
                # ...then update and add data
                self.reptor.api.projects.update_finding(
                    created_finding.id, finding.to_dict()
                )
            else:
                self.reptor.api.projects.create_finding(finding.to_dict())
            self.log.success(f'Pushed finding "{finding.data.title.value}"')

    def generate_findings(self) -> typing.List[Finding]:
        """Generates findings from the parsed input.

        The findings are generated from the `self.parsed_input` and are
        written to the `self.findings` list
        """
        if not self.parsed_input:
            self.parse()
        project_design = None
        self.findings = list()
        finding_methods = self._get_finding_methods()
        for method in finding_methods:
            finding = None
            finding_context = method(self)
            if finding_context is None:
                # Don't create finding if method returns None
                continue

            finding_name = method.__name__[len(self.FINDING_PREFIX) :]

            # Check if remote finding exists
            template_tag = f"{self.__class__.__name__.lower()}:{finding_name}"
            for finding_template in self.reptor.api.templates.search(template_tag):
                if template_tag in finding_template.tags:
                    # Take first matching template and fetch full data (search returns partial data only)
                    self.log.info(f"Found remote finding template for {template_tag}.")
                    finding_template = self.reptor.api.templates.get_template(
                        finding_template.id
                    )
                    # Get project language
                    language = self.reptor.api.projects.project.language
                    try:
                        translation = [
                            t
                            for t in finding_template.translations
                            if t.language == language
                        ][0]
                    except IndexError:
                        translation = [
                            t for t in finding_template.translations if t.is_main
                        ][0]
                        self.log.display(
                            f"No translation found for {language}. Taking main translation {translation.language}."
                        )

                    finding = Finding.from_translation(
                        translation, raise_on_unknown_fields=False
                    )
                    finding.template = finding_template.id
                    break

            if not finding:
                # Check if findings toml exists
                finding_dict = self.get_local_finding_data(finding_name)
                if not finding_dict:
                    self.log.warning(
                        f"Did not find finding template for {finding_name}. Creating default finding."
                    )
                    description = (
                        f"```{json.dumps(finding_context, indent=2)}```"
                        if finding_context
                        else "No description"
                    )
                    finding_dict = {
                        "data": {
                            "title": finding_name.replace("_", " ").title(),
                            "description": description,
                        },
                    }

                try:
                    finding = Finding(
                        finding_dict,
                        project_design=ProjectDesign(),
                        raise_on_unknown_fields=True,
                    )
                except ValueError:
                    self.log.info(
                        "Finding data not compatible with project design. Fetching project design from project."
                    )
                    project_design = self.reptor.api.project_designs.project_design
                    finding = Finding(
                        finding_dict,
                        project_design,
                        raise_on_unknown_fields=False,
                    )

            django_context = Context(finding_context)
            for finding_data in finding.data:
                # Iterate over all finding fields
                if isinstance(finding_data.value, list):
                    # Iterate over list to render list items
                    if finding_data.name == "affected_components":
                        finding_data.value = finding_context.get(
                            "affected_components", []
                        )
                        continue
                    finding_data_list = list()
                    for v in finding_data.value:
                        if content := Template(v.value).render(django_context):
                            finding_data_list.append(content)
                    finding_data.value = finding_data_list
                elif finding_data.value:
                    # If value not empty, render template
                    finding_data.value = Template(finding_data.value).render(
                        django_context
                    )
            self.findings.append(finding)
        return self.findings

    def get_local_finding_data(self, name: str) -> typing.Optional[dict]:
        """Loads a finding template from the local findings directory.

        Args:
            name: The name of the finding template to load

        Returns:
            A FindingRaw object or None if the template does not exist
        """
        if not self.finding_paths:
            self.debug("No path in finding_paths.")
            return None
        if not name.endswith(".toml"):
            name = f"{name}.toml"

        self.debug(
            f"Iterate through finding paths: {', '.join([str(p) for p in self.finding_paths])}"
        )
        for path in self.finding_paths:
            finding_template_path = path / name
            if os.path.isfile(finding_template_path):
                with open(finding_template_path, "rb") as f:
                    try:
                        finding_template = tomli.load(f)
                    except (tomli.TOMLDecodeError, TypeError):
                        self.log.warning(
                            f"Error while loading toml finding template {finding_template_path}."
                        )
                        continue
                return finding_template
            else:
                self.debug(f"No finding template found at {finding_template_path}.")
                continue
        return None
