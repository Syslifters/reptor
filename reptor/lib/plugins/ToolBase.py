import glob
import logging
import os
import sys
from xml.etree import ElementTree

from django.template.loader import render_to_string

import reptor.settings as settings
from reptor.api.NotesAPI import NotesAPI

from .Base import Base

log = logging.getLogger("reptor")


class ToolBase(Base):
    """The ToolBase provides plugin developers with all functionality that
    is commonly encountered when writing a plugin.


    Attributes:
        raw_input: Unformatted input, either from stdin or a file
        template: The .md file to be used during formatting
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.action = kwargs.get("action")
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None
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
    def set_template_vars(cls, plugin_path):
        template_paths = list()
        # Get template paths from plugin and userdir
        user_plugin_path = os.path.join(
            settings.PLUGIN_DIRS_USER, os.path.basename(plugin_path)
        )
        for path in [
            user_plugin_path,
            plugin_path,
        ]:  # Keep order: user templates override
            path = os.path.normpath(
                os.path.join(path, settings.PLUGIN_TEMPLATES_DIR_NAME)
            )
            if path not in template_paths:
                template_paths.append(path)

        # Add to paths if template paths exist
        cls.template_paths = [p for p in template_paths if os.path.isdir(p)]

        # Get template names from paths
        cls.templates = list()
        for path in cls.template_paths:
            templates = [
                os.path.basename(f).rsplit(".", 1)[0]
                for f in glob.glob(os.path.join(path, "*.md"))
            ]
            cls.templates.extend(
                [t for t in templates if t not in cls.templates])

        if cls.templates:
            # Choose default template
            if len(cls.templates) == 1:
                cls.template = cls.templates[0]
            else:
                default_templates = [
                    t for t in cls.templates if "default" in t]
                try:
                    cls.template = default_templates[0]
                except IndexError:
                    cls.template = cls.templates[0]

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        if plugin_filepath:
            cls.set_template_vars(os.path.dirname(plugin_filepath))
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
            [cls.parse_xml != ToolBase.parse_xml,
             cls.parse_json != ToolBase.parse_json,
             cls.parse_csv != ToolBase.parse_csv,]):
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

    def parse_xml(self):
        raise NotImplementedError(
            "Parse xml data is not implemented for this plugin.")

    def parse_json(self):
        raise NotImplementedError(
            "Parse json data is not implemented for this plugin.")

    def parse_csv(self):
        raise NotImplementedError(
            "Parse csv data is not implemented for this plugin.")

    def parse_raw(self):
        raise NotImplementedError(
            "Parse raw data is not implemented for this plugin.")

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
            if not self.file_path and self.raw_input:
                self.xml_root = ElementTree.fromstring(self.raw_input)
            else:
                self.xml_root = ElementTree.parse(self.file_path).getroot()
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

        self.formatted_input = render_to_string(
            f"{self.template}.md", {"data": self.parsed_input}
        )
        # TODO there might be a more elegant solution, maybe.
        while '\n\n\n' in self.formatted_input:
            self.formatted_input = self.formatted_input.replace(
                '\n\n\n', '\n\n')

    def upload(self):
        """Uploads the `self.formatted_input` to sysreptor via the NotesAPI."""
        if not self.formatted_input:
            self.format()
        notename = self.notename or self.__class__.__name__.lower()
        parent_notename = "Uploads" if notename != "Uploads" else None

        NotesAPI(self.reptor).write_note(
            notename=notename,
            parent_notename=parent_notename,
            content=self.formatted_input,
            icon=self.note_icon,
            no_timestamp=self.no_timestamp,
            force_unlock=self.force_unlock,
        )
