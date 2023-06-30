import sys
import logging
from api.NotesAPI import NotesAPI
from classes.Base import Base
from utils.conf import config

log = logging.getLogger('reptor')


class ToolBase(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call = kwargs.get('call')
        self.note_icon = "🛠️"
        self.raw_input = None
        self.parsed_input = None
        self.formatted_input = None
        self.no_timestamp = config['cli'].get('no_timestamp')
        self.force_unlock = config['cli'].get('force_unlock')

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
        parent_notename = 'Uploads' if notename != 'Uploads' else None

        NotesAPI().write_note(
            notename=notename,
            parent_notename=parent_notename,
            content=self.formatted_input,
            icon=self.note_icon,
            no_timestamp=self.no_timestamp,
            force_unlock=self.force_unlock,
        )
