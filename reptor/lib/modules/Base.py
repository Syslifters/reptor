from reptor.lib.interfaces.conf import ConfigProtocol
from reptor.lib.interfaces.reptor import ReptorProtocol

from reptor.lib.logger import reptor_logger, ReptorAdapter


class Base:
    config: ConfigProtocol
    reptor: ReptorProtocol
    logger: ReptorAdapter = reptor_logger

    def __init__(self, reptor: ReptorProtocol, **kwargs):
        self.notename = kwargs.get("notename")
        self.file_path = kwargs.get("file", "")
        self.reptor = reptor
        self.config = self.reptor.get_config()

    @classmethod
    def add_arguments(cls, parser):
        pass

    def run(self):
        pass
