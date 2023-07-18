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
        """Access the logging directly from plugin

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

    def run(self):
        pass
