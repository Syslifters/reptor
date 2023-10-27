import os
import sys
import typing

from reptor.lib.console import reptor_console
from reptor.lib.reptor import Reptor


class Base:
    """
    Provides all bases with access to the Reptor app.

    Attributes:
        reptor: Reptor Instance
        notetitle: The Notename to be used when uploading
    """

    reptor: Reptor
    meta: typing.Dict = {
        "name": "",
        "author": "",
        "version": "",
        "website": "",
        "license": "",
        "tags": [],
        "summary": "",
    }

    keys: typing.Dict = {}

    def __init__(self, **kwargs):
        self.notetitle = kwargs.get("notetitle")
        self.file_path = kwargs.get("file", "")
        self.reptor = kwargs.get("reptor", None)

        plugin_name = self.__class__.__name__.lower()
        for plugin_config_key in self.reptor.get_config().get_config_keys(
            plugin=plugin_name
        ):
            if not hasattr(self, plugin_config_key):
                self.__setattr__(
                    plugin_config_key,
                    self.reptor.get_config().get(plugin_config_key, plugin=plugin_name),
                )

        self._check_required_keys_are_set(plugin_name)

    def _check_required_keys_are_set(self, plugin_name: str = ""):
        """This method will check if the keys specified in the attribute keys
        are present in the config. If they are not present in the config, it will
        over the user to set them.

        The form of each key should be key:help , i.e:

        ```
        {
            "api_secret": "Used to connect to the API",
            "language": "default language of the source items"
        }
        ```
        """
        config_updated = False
        for key in self.keys:
            config_value = self.reptor.get_config().get(key, "", plugin=plugin_name)
            if not config_value:
                self.console.print(
                    f"[red]Required Key {key} not set in config. [bold]Set it now to continue or press ENTER to exit:[/bold][/red]"
                )
                config_value = input()
                if not config_value:
                    self.console.print("[green]Exiting...[/green]")
                    sys.exit(0)
                self.reptor.get_config().set(key, config_value, plugin=plugin_name)
                config_updated = True

        if config_updated:
            self.reptor.get_config().store_config()

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

    def deliver_file(
        self,
        content: bytes,
        filename: str,
        upload: bool = False,
        stdout: bool = False,
    ) -> None:
        if stdout:
            # Write to stdout
            stdout = True
            sys.stdout.buffer.write(content)
        elif upload:
            notetitle = "Uploads"
            self.reptor.api.notes.upload_file(
                content=content, filename=filename, notetitle=notetitle
            )
            self.log.success(f'Uploaded "{filename}" to "{notetitle}" note')
        else:
            # Check if filename exists on disk
            if os.path.exists(filename):
                raise FileExistsError(f'"{filename}" exists. Rename or delete it.')
            with open(filename, "wb") as f:
                f.write(content)
            self.log.success(f"Exported to {filename}")

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

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
