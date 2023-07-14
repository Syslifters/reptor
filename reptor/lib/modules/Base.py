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

        plugin_name = self.__class__.__name__.lower()
        for plugin_config_key in self.config.get_config_keys(plugin=plugin_name):
            self.__setattr__(plugin_config_key, self.config.get(
                plugin_config_key, plugin=plugin_name))

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        pass

    def run(self):
        pass
