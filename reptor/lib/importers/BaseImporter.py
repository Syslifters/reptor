import typing

from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.api.models import FindingTemplate, FindingDataRaw
from reptor.api.TemplatesAPI import TemplatesAPI

from reptor.lib.console import reptor_console


class BaseImporter:
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

    @property
    def log(self):
        """Access the logging directly from importer

        Returns:
            ReptorAdapter: Logging Module
        """
        return self.reptor.get_logger()

    @property
    def console(self):
        """Access the rich console that allows markdown etc.

        Returns:
            Console: rich console
        """
        return reptor_console

    def success(self, msg, *args, **kwargs):
        """Use this to print Green text by default. You can change colors etc.

        See the logger.py for examples.

        Args:
            msg (str): Any message you want to print
        """
        self.log.success(msg, *args, **kwargs)

    def display(self, msg, *args, **kwargs):
        """Use this to print blue text by default. You can change colors etc.

        See the logger.py for examples.

        Args:
            msg (str): Any message you want to print
        """
        self.log.display(msg, *args, **kwargs)

    def highlight(self, msg, *args, **kwargs):
        """Prints a yellow message. Good for highlighting certain
        output.

        Args:
            msg (str): Any message you want to print
        """
        self.log.highlight(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Default DEBUG method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in DEBUG log
        """
        self.log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Default INFO method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in INFO log
        """
        self.log.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Default WARNING method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in WARNING log
        """
        self.log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Default ERROR method of the logger. Use this instead of accessing
        log or reptor.get_logger()

        Args:
            msg (str): Message to show in ERROR log
        """
        self.log.error(msg, *args, **kwargs)

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
