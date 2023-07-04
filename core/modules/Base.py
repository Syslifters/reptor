from core.interfaces.conf import ConfigProtocol
from core.interfaces.reptor import ReptorProtocol


class Base:
    config: ConfigProtocol
    reptor: ReptorProtocol

    def __init__(self, reptor: ReptorProtocol, **kwargs):
        self.notename = kwargs.get("notename")
        self.reptor = reptor
        self.config = self.reptor.get_config()

    @classmethod
    def add_arguments(cls, parser):
        pass

    def run(self):
        pass
