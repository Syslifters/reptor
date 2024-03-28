import glob
import json
import logging
import os
import sys
import typing
from functools import cached_property
from pathlib import Path
from xml.etree import ElementTree

import tomli
import xmltodict
from django.template import Context, Template
from django.template.loader import render_to_string

import reptor.settings as settings
from reptor.models.Finding import Finding
from reptor.models.FindingTemplate import FindingTemplate
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
    supports_multi_input = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conf = kwargs.get("conf")
        self.action = kwargs.get("action")
        self.notetitle = self.notetitle or self.plugin_name
        self.push_findings = kwargs.get("push_findings")
        self.input = kwargs.get("input")
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None
        self.note_templates = None
        self.findings = []
        self.timestamp = (
            not self.reptor.get_config().get("cli", dict()).get("no_timestamp")
        )

        self.input_format = kwargs.get("format")
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
    def get_filenames_from_paths(
        cls, dir_paths: typing.List[Path], filetype: str
    ) -> typing.List[str]:
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

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        if plugin_filepath:
            cls.setup_class(Path(os.path.dirname(plugin_filepath)))

        parser.add_argument(
            "-i",
            "--input",
            action="store",
            dest="input",
            default=None,
            nargs="*" if cls.supports_multi_input else "?",
            help=f"Input file, if not stdin {'(multiple files allowed)' if cls.supports_multi_input else ''}",
        )

        action_group = parser.add_mutually_exclusive_group()
        action_group.title = "action_group"
        if cls.create_notes != ToolBase.create_notes:
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
            action_group.add_argument(
                "--template-vars",
                "--template-variables",
                action="store_const",
                dest="action",
                const="template-vars",
                help="Print template variables (needed for finding template customization).",
            )
        action_group.add_argument(
            "--parse",
            action="store_const",
            dest="action",
            const="parse",
            default="format",
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
        if cls.get_filenames_from_paths(cls.finding_paths, "toml"):
            # If finding templates exist
            action_group.add_argument(
                "--upload-finding-templates",
                action="store_const",
                dest="action",
                const="upload-finding-templates",
                help="Upload local finding templates to SysReptor",
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
            if self.parsed_input is not None:
                self.print(json.dumps(self.parsed_input, indent=2))
        elif self.action == "template-vars":
            self.parse()
            if p := self.preprocess_for_template():
                self.print(json.dumps(p, indent=2))
        elif self.action == "format":
            self.format()
            if self.formatted_input is not None:
                self.print(self.formatted_input)
        elif self.action == "upload":
            self.upload()
        elif self.action == "upload-finding-templates":
            self.upload_finding_templates()

    def load(self):
        """Puts the input into raw_input"""
        if self.input:
            self.raw_input = list()
            for filepath in self.input:
                with open(filepath, "r") as f:
                    self.raw_input.append(f.read())
            if len(self.raw_input) == 1:
                self.raw_input = self.raw_input[0]
                self.input = None
        else:
            self.display("Reading from stdin...")
            self.raw_input = sys.stdin.read()

    def parse_xml(self, as_dict=True):
        if as_dict:
            if isinstance(self.raw_input, list):
                self.parsed_input = list()
                for raw_input in self.raw_input:
                    self.parsed_input.append(xmltodict.parse(raw_input))
            else:
                self.parsed_input = xmltodict.parse(self.raw_input)  # type: ignore
        else:
            if isinstance(self.raw_input, list):
                self.xml_root = list()
                for raw_input in self.raw_input:
                    self.xml_root.append(ElementTree.fromstring(raw_input))
            else:
                self.xml_root = ElementTree.fromstring(self.raw_input)

    def parse_json(self):
        if isinstance(self.raw_input, list):
            self.parsed_input = list()
            for raw_input in self.raw_input:
                self.parsed_input.append(json.loads(raw_input))
        else:
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
        if not self.raw_input:
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
        """
        if not self.parsed_input:
            self.parse()

        if data := self.create_notes():
            if isinstance(data, NoteTemplate):
                data = [data]
            self.note_templates = data
            self.formatted_input = self.format_note_template(data)
            return
        self.log.warning(
            f"`create_notes` didn't return data for {self.plugin_name} plugin."
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
        raise NotImplementedError("Create notes is not implemented for this plugin.")

    def upload_finding_templates(self):
        finding_template_names = self.get_filenames_from_paths(
            self.finding_paths, "toml"
        )
        uploaded = 0
        for name in finding_template_names:
            if finding := self.get_local_finding_template(name):
                template_tag = f"{self.plugin_name}:{name}"
                remote_template = self.reptor.api.templates.get_templates_by_tag(
                    template_tag
                )
                if remote_template:
                    self.log.display(
                        f"Finding template with tag {template_tag} already exists. Skipping."
                    )
                    continue
                uploaded += 1
                finding["is_main"] = True
                finding = FindingTemplate(
                    {"translations": [finding], "tags": ["reptor", template_tag]}
                )
                self.reptor.api.templates.upload_template(finding)
                self.log.display(f'Uploaded finding template "{name}".')
        if uploaded:
            self.log.success(
                f"Successfully uploaded {uploaded} finding template{'s'[:uploaded^1]}."
            )

    def upload(self):
        """Uploads the `self.formatted_input` to sysreptor via the NotesAPI."""
        if not self.formatted_input:
            self.format()

        if self.note_templates:
            self.reptor.api.notes.write_note_templates(
                self.note_templates, timestamp=self.timestamp
            )
        else:
            parent_notetitle = "Uploads" if self.notetitle != "Uploads" else None
            self.reptor.api.notes.write_note(
                title=self.notetitle,
                text=self.formatted_input,
                parent_notetitle=parent_notetitle,
                icon_emoji=self.note_icon,
                timestamp=self.timestamp,
            )
        self.log.success("Successfully uploaded to notes.")

    def generate_and_push_findings(self) -> None:
        self.generate_findings()
        if len(self.findings) == 0:
            self.log.display("No findings generated.")
            return
        project_findings = [
            Finding(f, self._project_design)
            for f in self.reptor.api.projects.get_findings()
        ]
        project_finding_titles = [f.data.title.value for f in project_findings]
        for finding in self.findings:
            self.log.info(f'Checking if finding "{finding.data.title.value}" exists')
            if finding.data.title.value in project_finding_titles:
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

    @cached_property
    def _project_language(self) -> str:
        return self.reptor.api.projects.project.language

    @cached_property
    def _project_design(self) -> ProjectDesign:
        return self.reptor.api.project_designs.project_design

    def _get_finding_from_remote_template(
        self, template_tag: str
    ) -> typing.Optional[Finding]:
        """
        Returns first remote finding template with matching tag.
        """
        for finding_template in self.reptor.api.templates.get_templates_by_tag(
            template_tag
        ):
            # Take first matching template and fetch full data (search returns partial data only)
            self.log.info(f"Found remote finding template for {template_tag}.")
            finding_template = self.reptor.api.templates.get_template(
                finding_template.id
            )

            try:
                translation = [
                    t
                    for t in finding_template.translations
                    if t.language == self._project_language
                ][0]
            except IndexError:
                translation = [t for t in finding_template.translations if t.is_main][0]
                self.log.display(
                    f"No translation found for {self._project_language}. Taking main translation {translation.language}."
                )

            finding = Finding.from_translation(
                translation,
                project_design=self._project_design,
                raise_on_unknown_fields=False,
            )
            finding.template = finding_template.id

            return finding

    def _get_finding_from_local_template(self, name: str) -> typing.Optional[Finding]:
        # Check if findings toml exists
        finding_dict = self.get_local_finding_template(name)
        if not finding_dict:
            return None

        try:
            finding = Finding(
                finding_dict,
                project_design=self._project_design,
                raise_on_unknown_fields=False,
            )
        except ValueError:
            self.log.error("Finding data incompatible with project design.")
            return None
        return finding

    def generate_findings(self) -> typing.List[Finding]:
        """Generates findings from the parsed input.

        The findings are generated from the `self.parsed_input` and are
        written to the `self.findings` list
        """
        if not self.parsed_input:
            self.parse()
        self.findings = list()
        finding_methods = self._get_finding_methods()

        for method in finding_methods:
            finding = None
            finding_contexts = method(self)
            if finding_contexts is None:
                # Don't create finding if method returns None
                continue
            if not isinstance(finding_contexts, list):
                finding_contexts = [finding_contexts]

            for finding_context in finding_contexts:
                finding_names = list()
                if t := finding_context.get("finding_templates"):
                    if not isinstance(t, list):
                        t = [t]
                    finding_names.extend(t)
                t = method.__name__[len(self.FINDING_PREFIX) :]
                if t not in finding_names:
                    finding_names.append(t)

                for finding_name in finding_names:
                    # Check if remote finding template exists
                    template_tag = f"{self.plugin_name}:{finding_name}"
                    finding = self._get_finding_from_remote_template(template_tag)

                    # If not, check if local finding template exists
                    if not finding:
                        finding = self._get_finding_from_local_template(finding_name)
                    if finding:
                        break
                if not finding:
                    continue

                django_context = Context(finding_context, autoescape=False)
                for finding_data in finding.data:
                    # Iterate over all finding fields
                    if finding_data.value:
                        if finding_data.type in ["markdown", "string", "cvss"]:
                            # Render template
                            finding_data.value = Template(finding_data.value).render(
                                django_context
                            )
                    elif finding_data.type in [
                        "list",
                        "enum",
                        "combobox",
                        "date",
                        "number",
                        "boolean",
                    ]:
                        if value := finding_context.get(finding_data.name):
                            try:
                                finding_data.value = value
                            except ValueError:
                                log.warning(
                                    f'Invalid value "{finding_data.value}" for field "{finding_data.name}"'
                                )

                self.findings.append(finding)
        return self.findings

    def get_local_finding_template(self, name: str) -> typing.Optional[dict]:
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

    @staticmethod
    def cvss2_to_3(cvss2: str) -> str:
        if cvss2.startswith("CVSS:3") or cvss2.startswith("CVSS:4"):
            return cvss2

        cvss2 = cvss2.replace("CVSS2#", "")
        cvss2_metrics = {
            k: v for k, v in (item.split(":") for item in cvss2.split("/"))
        }
        cvss3 = dict()
        # base
        cvss3["AV"] = cvss2_metrics.get("AV", "N")
        cvss3["AV"] = cvss3["AV"] if cvss3["AV"] in ["L", "A", "P", "N"] else "N"
        cvss3["AC"] = cvss2_metrics.get("AC", "L")
        cvss3["AC"] = cvss3["AC"] if cvss3["AC"] in ["H", "L"] else "L"
        auth_mapping = {
            "M": "H",
            "S": "L",
            "N": "N",
        }
        cvss3["PR"] = auth_mapping.get(cvss2_metrics.get("Au", "N"), "N")
        cvss3["UI"] = "N"
        cvss3["S"] = "U"
        impact_mapping = {
            "C": "H",
            "P": "L",
            "N": "N",
        }
        cvss3["C"] = impact_mapping.get(cvss2_metrics.get("C", "N"), "N")
        cvss3["I"] = impact_mapping.get(cvss2_metrics.get("I", "N"), "N")
        cvss3["A"] = impact_mapping.get(cvss2_metrics.get("A", "N"), "N")
        return f"CVSS:3.1/{'/'.join([f'{k}:{v}' for k, v in cvss3.items()])}"
