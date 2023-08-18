import glob
import json
import logging
import os
import sys
import typing
from pathlib import Path
from xml.etree import ElementTree

import toml
import xmltodict
from django.template import Context, Template
from django.template import base as django_base
from django.template.loader import render_to_string

from reptor.utils.django_tags import django_tags
import reptor.settings as settings
from reptor.models.Finding import FindingRaw

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
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None
        self.findings = None
        self.no_timestamp = (
            self.reptor.get_config().get("cli", dict()).get("no_timestamp")
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
            dir_path = os.path.normpath(Path(path) / dirname)

            if dir_path not in dir_paths and os.path.isdir(dir_path):
                dir_paths.append(Path(dir_path))

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
        return files_from_plugin_dir

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
        cls.template = None
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
        super().add_arguments(parser, plugin_filepath)
        if plugin_filepath:
            cls.setup_class(Path(os.path.dirname(plugin_filepath)))
        if cls.templates:
            parser.add_argument(
                "-t",
                "--template",
                action="store",
                default=cls.template,
                choices=cls.templates,
                help="Template for output formatting",
            )

        action_group = parser.add_mutually_exclusive_group()
        action_group.title = "action_group"
        action_group.add_argument(
            "-parse",
            "--parse",
            action="store_const",
            dest="action",
            const="parse",
            default="format",
        )
        action_group.add_argument(
            "-format",
            "--format",
            action="store_const",
            dest="action",
            const="format",
            default="format",
        )
        action_group.add_argument(
            "-upload",
            "--upload",
            action="store_const",
            dest="action",
            const="upload",
            default="format",
        )

        if any(
            [
                cls.parse_xml != ToolBase.parse_xml,
                cls.parse_json != ToolBase.parse_json,
                cls.parse_csv != ToolBase.parse_csv,
            ]
        ):
            input_format_group = parser.add_mutually_exclusive_group()
            input_format_group.title = "input_format_group"
        # Add parsing options only if implemented by modules
        if cls.parse_xml != ToolBase.parse_xml:
            input_format_group.add_argument(
                "-xml",
                "--xml",
                action="store_const",
                dest="format",
                const="xml",
                default="raw",
            )
        if cls.parse_json != ToolBase.parse_json:
            input_format_group.add_argument(
                "-json",
                "--json",
                action="store_const",
                dest="format",
                const="json",
                default="raw",
            )
        if cls.parse_csv != ToolBase.parse_csv:
            input_format_group.add_argument(
                "-csv",
                "--csv",
                action="store_const",
                dest="format",
                const="csv",
                default="raw",
            )

    def run(self):
        """
        The run method is always called by the main reptor application.

        The flow is:

        Parsing -> Formatting -> Uploading
        """
        if self.action == "parse":
            self.parse()
            self.reptor.logger.display(self.parsed_input)
        elif self.action == "format":
            self.format()
            self.reptor.logger.display(self.formatted_input)
        elif self.action == "upload":
            self.upload()

    def load(self):
        """Puts the stdin into raw_input"""
        self.raw_input = sys.stdin.read()

    def parse_xml(self, as_dict=True):
        if as_dict:
            self.parsed_input = xmltodict.parse(self.raw_input)
        else:
            if not self.file_path and self.raw_input:
                self.xml_root = ElementTree.fromstring(self.raw_input)
            else:
                self.xml_root = ElementTree.parse(self.file_path).getroot()

    def parse_json(self):
        self.parsed_input = json.loads(self.raw_input)

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

        data = self.process_parsed_input_for_template()
        self.formatted_input = render_to_string(f"{self.template}.md", data)

    def process_parsed_input_for_template(self):
        return {"data": self.parsed_input}

    def upload(self):
        """Uploads the `self.formatted_input` to sysreptor via the NotesAPI."""
        if not self.formatted_input:
            self.format()
        notename = self.notename or self.__class__.__name__.lower()
        parent_notename = "Uploads" if notename != "Uploads" else ""

        self.reptor.api.notes.write_note(
            self.formatted_input,
            notename=notename,
            parent_notename=parent_notename,
            icon=self.note_icon,
            no_timestamp=self.no_timestamp,
            force_unlock=self.force_unlock,
        )

    def generate_findings(self) -> typing.List[FindingRaw]:
        """Generates findings from the parsed input.

        The findings are generated from the `self.parsed_input` and are
        written to the `self.findings` list
        """
        if not self.parsed_input:
            self.parse()
        self.findings = list()
        finding_methods = [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and func.startswith(self.FINDING_PREFIX)
        ]
        for method in finding_methods:
            finding_context = getattr(self, method)()
            if finding_context is None:
                # Don't create finding if method returns None
                continue

            finding_name = method[len(self.FINDING_PREFIX) :]
            # TODO: Check if remote finding exists
            # Check if findings toml exists
            finding = self.get_finding_from_local_template(finding_name)
            if not finding:
                self.log.warning(
                    f"Did not find finding template for {finding_name}. Creating default finding."
                )
                description = (
                    f"```{json.dumps(finding_context, indent=2)}```"
                    if finding_context
                    else "No description"
                )
                finding = FindingRaw(
                    {
                        "data": {
                            "title": finding_name.replace("_", " ").title(),
                            "description": description,
                        },
                    }
                )

            # TODO Django rendering
            finding_context = Context(finding_context)
            for k, v in finding.data.to_json().items():
                # TODO: Complex data types
                with django_tags(format="html"):
                    setattr(finding.data, k, Template(v).render(finding_context))
                pass

            self.findings.append(finding)

        return self.findings

    def get_finding_from_local_template(self, name: str) -> typing.Optional[FindingRaw]:
        """Loads a finding template from the local findings directory.

        Args:
            name: The name of the finding template to load

        Returns:
            A FindingRaw object or None if the template does not exist
        """
        if not self.finding_paths:
            return None
        if not name.endswith(".toml"):
            name = f"{name}.toml"

        for path in self.finding_paths:
            finding_template_path = path / name
            if os.path.isfile(finding_template_path):
                with open(finding_template_path, "r") as f:
                    try:
                        finding_template = toml.load(f)
                    except (toml.TomlDecodeError, TypeError) as e:
                        self.log.warning(
                            f"Error while loading toml finding template {name}."
                        )
                        return None
                return FindingRaw(finding_template)
        return None
