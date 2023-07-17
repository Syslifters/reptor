import typing
from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.lib.console import reptor_console


class Base:
    """
    Provides all bases with access to the Reptor app.

    Attributes:
        reptor: Reptor Instance
        notename: The Notename to be used when uploading
    """

    reptor: ReptorProtocol
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
        self.notename = kwargs.get("notename")
        self.file_path = kwargs.get("file", "")
        self.reptor = kwargs.get("reptor", None)

        plugin_name = self.__class__.__name__.lower()
        for plugin_config_key in self.reptor.get_config().get_config_keys(
            plugin=plugin_name
        ):
            self.__setattr__(
                plugin_config_key,
                self.reptor.get_config().get(plugin_config_key, plugin=plugin_name),
            )

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        pass

    @property
    def log(self):
        return self.reptor.get_logger()

    @property
    def console(self):
        return reptor_console

    def display(self, msg, *args, **kwargs):
        self.log.display(msg, *args, **kwargs)

    def highlight(self, msg, *args, **kwargs):
        self.log.highlight(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log.error(msg, *args, **kwargs)

    def run(self):
        pass
