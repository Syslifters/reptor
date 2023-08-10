import typing

from reptor.api.models import FindingDataRaw, FindingTemplate
from reptor.lib.console import reptor_console
from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.lib.plugins.Base import Base


class BaseImporter(Base):
    reptor: ReptorProtocol
    mapping: typing.Dict
    meta: typing.Dict = {
        "name": "",
        "author": "",
        "version": "",
        "website": "",
        "license": "",
        "tags": [],
        "summary": "",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reptor = kwargs.get("reptor", None)
        self.finding_language = kwargs.get("language", "en-US")
        self.is_main_language = kwargs.get("main", True)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        action_group = parser.add_argument_group()
        action_group.title = "Global Importer Settings"
        action_group.add_argument(
            "-l",
            "--language",
            metavar="LANGUAGE",
            action="store",
            const="en-US",
            nargs="?",
            help="Language of Finding i.e en-US, default is en-US",
        )
        action_group.add_argument(
            "-main",
            "--main",
            action="store_true",
            help="Is this the main template language? Default True",
        )

    def next_findings_batch(self):
        """Implement this to yield the next findings to process"""
        return None

    def _create_finding_item(self, raw_data: typing.Dict) -> FindingTemplate:
        remapped_data = dict()
        for key, value in self.mapping.items():
            converted_data = raw_data[key]
            # check if we have a convert_method and call it
            # update the value
            convert_method_name = f"convert_{key}"
            if hasattr(self, convert_method_name):
                if callable(getattr(self, convert_method_name)):
                    converter_method = getattr(self, convert_method_name)
                    self.debug(f"Calling: {convert_method_name}")
                    converted_data = converter_method(raw_data[key])

            remapped_data[value] = converted_data

        new_finding = FindingTemplate(remapped_data)
        new_finding.data = FindingDataRaw(remapped_data)
        return new_finding

    def _upload_finding_templates(self, new_finding: FindingTemplate):
        self.debug(f"Is main language?: {self.is_main_language}")
        updated_template = self.reptor.api.templates.upload_new_template(
            new_finding,
            language=self.finding_language,
            is_main_language=self.is_main_language,
        )
        if updated_template:
            self.display(f"Uploaded {updated_template.id}")
        else:
            self.error("Do you want to abort? [Y/n]")
            abort_answer = input()[:1].lower()
            if abort_answer != "n":
                raise AssertionError("Aborting")

    def run(self):
        if not self.mapping:
            raise ValueError("You need to provide a mapping.")

        for external_finding in self.next_findings_batch():  # type: ignore
            new_finding = self._create_finding_item(external_finding)
            if not new_finding:
                continue
            self.display(f"Uploading {new_finding.data.title}")
            self.debug(new_finding)
            self._upload_finding_templates(new_finding)
