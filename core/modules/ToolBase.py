import sys
import logging

from xml.etree import ElementTree

from api.NotesAPI import NotesAPI

from .Base import Base

log = logging.getLogger("reptor")


class ToolBase(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call = kwargs.get("call")
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None
        self.no_timestamp = self.config.get("cli").get("no_timestamp")
        self.force_unlock = self.config.get("cli").get("force_unlock")

        self.input_format = kwargs.get("format")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "-c", "--call", default="format", choices=["parse", "format", "upload"]
        )

        parser.add_argument(
            "-format", "--format", choices=["xml", "json", "csv", "raw"], default="raw"
        )

    def run(self):
        if self.call == "parse":
            self.parse()
            print(self.parsed_input)
        elif self.call == "format":
            self.format()
            print(self.formatted_input)
        elif self.call == "upload":
            self.upload()

    def load(self):
        self.raw_input = sys.stdin.read()

    def parse_xml(self, xml_root: ElementTree.Element):
        ...

    def parse_json(self):
        ...

    def parse_csv(self):
        ...

    def parse(self):
        if not self.raw_input and not self.file_path:
            self.load()

        if self.input_format == "xml":
            if not self.file_path and self.raw_input:
                xml_root = ElementTree.fromstring(self.raw_input)
            else:
                xml_root = ElementTree.parse(self.file_path).getroot()
            self.parse_xml(xml_root)

        elif self.input_format == "json":
            self.parse_json()
        elif self.input_format == "csv":
            self.parse_csv()

    def format(self):
        if not self.parsed_input:
            self.parse()

    def upload(self):
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
