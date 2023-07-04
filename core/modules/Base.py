from core.reptor import Reptor
from core.conf import Config


class Base:
    config: Config
    reptor: Reptor

    def __init__(self, **kwargs):
        self.notename = kwargs.get("notename")
        self.reptor = Reptor.instance
        self.config = self.reptor.get_config()

    @classmethod
    def add_arguments(cls, parser):
        pass

    def run(self):
        pass
