import sys
import logging
from utils.api import write_note
from classes.Base import Base

log = logging.getLogger('reptor')


class ToolBase(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call = kwargs.get('call')
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument('-c', '--call',
                            default='format',
                            choices=['parse', 'format', 'upload'])

    def run(self):
        if self.call == 'parse':
            self.parse()
            print(self.parsed_input)
        elif self.call == 'format':
            self.format()
            print(self.formatted_input)
        elif self.call == 'upload':
            self.upload()

    def load(self):
        self.raw_input = sys.stdin.read()

    def parse(self):
        if not self.raw_input:
            self.load()

    def format(self):
        if not self.parsed_input:
            self.parse()

    def upload(self):
        if not self.formatted_input:
            self.format()
        notename = self.notename or self.__class__.__name__.lower()
        parent = 'Uploads' if notename != 'Uploads' else None
        write_note(
            notename=notename,
            parent=parent,
            content=self.formatted_input,
            icon=self.note_icon)
