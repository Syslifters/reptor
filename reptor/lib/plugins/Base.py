from reptor.lib.interfaces.reptor import ReptorProtocol


class Base:
    """
    Provides all bases with access to the Reptor app.

    Attributes:
        reptor: Reptor Instance
        notename: The Notename to be used when uploading
    """

    reptor: ReptorProtocol

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

    def run(self):
        pass
