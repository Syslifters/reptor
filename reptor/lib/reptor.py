import argparse
import logging
import sys

import django
from django.conf import settings as django_settings
import reptor.settings as settings
import reptor.subcommands as subcommands
from reptor.lib.conf import Config
from reptor.lib.console import Console, reptor_console
from reptor.lib.logger import ReptorAdapter, reptor_logger
from reptor.lib.plugins.DocParser import PluginDocs
from reptor.utils.markdown import convert_markdown_to_console
from reptor.lib.pluginmanager import PluginManager

from .interfaces.reptor import ReptorProtocol

root_logger = logging.getLogger("root")

# Todo:
# - Refactor Global and Configuration arguments
# - Refactor Output


class Reptor(ReptorProtocol):
    _config: Config
    _parser: argparse.ArgumentParser
    _sub_parsers: argparse._SubParsersAction
    plugin_manager: PluginManager

    logger: ReptorAdapter = reptor_logger
    console: Console = reptor_console

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Reptor, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._load_config()

        self.plugin_manager = PluginManager(self)

        # Todo: Debate if always write to file or togglable
        self.logger.add_file_log()

    def get_config(self) -> Config:
        """Use this to access the current config

        Returns:
            Config: Current Configuration
        """
        return self._config

    def _load_config(self) -> None:
        """Load the config into Reptor"""
        self._config = Config()
        self._config.load_config()

    def _create_parsers(self):
        """Creates the description in the help and the parsers to be used

        Returns:
            parser,subparsers: ArgumentParser and SubParser
        """
        # Argument parser description
        description = ""
        for (
            short_help_class,
            short_help_group_meta,
        ) in subcommands.SUBCOMMANDS_GROUPS.items():
            description += f"\n{short_help_group_meta[0]}:\n"

            item: PluginDocs
            for item in short_help_group_meta[1]:
                description += f"{item.name:<21} {item.short_help}{settings.NEWLINE}"

        # Argument parser
        self._parser = argparse.ArgumentParser(
            prog="reptor", formatter_class=argparse.RawDescriptionHelpFormatter
        )

        self._sub_parsers = self._parser.add_subparsers(
            dest="command", description=description, help=argparse.SUPPRESS
        )

    def _dynamically_add_plugin_options(self):
        # Dynamically add plugin options
        for name, plugin in self.plugin_manager.LOADED_PLUGINS.items():
            plugin.subparser = self._sub_parsers.add_parser(
                name,
                description=plugin.description,
                formatter_class=argparse.RawTextHelpFormatter,
            )
            plugin.loader.add_arguments(
                plugin.subparser, plugin_filepath=plugin.__file__
            )

    def _add_config_parse_options(self):
        """Creates the configuration arguments

        Args:
            parser (argparse.ArgumentParser): main parser
        """
        config_parser = self._parser.add_argument_group("configuration")
        config_parser.add_argument("-s", "--server")
        config_parser.add_argument("-t", "--token", help="SysReptor API token")
        config_parser.add_argument(
            "-f",
            "--force-unlock",
            help="force unlock notes and sections",
            action="store_true",
        )
        config_parser.add_argument(
            "--insecure", help="do not verify server certificate", action="store_true"
        )
        private_or_project_parser = config_parser.add_mutually_exclusive_group()
        private_or_project_parser.add_argument(
            "-p", "--project-id", help="SysReptor project ID"
        )
        private_or_project_parser.add_argument(
            "--private-note", help="add notes to private notes", action="store_true"
        )

    def _configure_global_arguments(self):
        """Enables the parameters
        - project_id
        - verbose
        - insecure
        """
        self._parser.add_argument(
            "-v",
            "--verbose",
            help="increase output verbosity (> INFO)",
            action="store_true",
        )
        self._parser.add_argument(
            "--debug", help="sets logging to DEBUG", action="store_true"
        )
        self._parser.add_argument("-n", "--notename")
        self._parser.add_argument(
            "-nt",
            "--no-timestamp",
            help="do not prepent timestamp to note",
            action="store_true",
        )

        self._parser.add_argument("-file", "--file", help="Local file to read")
        return self._parser

    def _parse_main_arguments_with_subparser(self):
        # Parse main parser arguments also if provided in subparser
        previous_unknown = None
        args, unknown = self._parser.parse_known_args()
        while len(unknown) and unknown != previous_unknown:
            args, unknown = self._parser.parse_known_args(unknown, args)
            previous_unknown = unknown

        if args.verbose:
            reptor_logger.logger.setLevel(logging.INFO)
            root_logger.setLevel(logging.INFO)

        if args.debug:
            reptor_logger.logger.setLevel(logging.DEBUG)
            root_logger.setLevel(logging.DEBUG)

        # Override conf from config file by CLI
        args_dict = vars(args)
        config = Config()
        for k in ["server", "project_id", "token", "insecure"]:
            config.set(k, args_dict.get(k) or config.get(k, ""))
        # Add cli options to config/cli
        config.set("cli", args_dict)

        self.logger.debug(f"Parsed args: {args}")
        return args

    def _print_title(self):
        """Prints a parsed & converted markdown text from title.md in the root directory"""
        with open(settings.BASE_DIR / "title.md", "r", encoding="utf-8") as f:
            reptor_console.print(convert_markdown_to_console(f.read()))

    def run(self) -> None:
        """The run method actually starts the cli application"""
        # Todo: Refactor the order when the parsers are available. Otherwise
        # with the current direction we don't have --debug and -verbose output
        # until we hit self._parse_main_arguments_with_subparser()
        self.logger.info("Reptor is starting...")

        # Todo: remove current hack for debug and verbose logging
        if "-v" in sys.argv or "--verbose" in sys.argv:
            reptor_logger.logger.setLevel(logging.INFO)
            root_logger.setLevel(logging.INFO)
        if "--debug" in sys.argv:
            reptor_logger.logger.setLevel(logging.DEBUG)
            root_logger.setLevel(logging.DEBUG)

        self.plugin_manager.run_loading_sequence()

        self.plugin_manager.load_plugins()

        django_settings.configure(settings, DEBUG=True)
        django.setup()
        self._create_parsers()

        self._dynamically_add_plugin_options()

        # Static module options
        self._add_config_parse_options()

        self._configure_global_arguments()
        args = self._parse_main_arguments_with_subparser()

        # Subcommands
        if args.command in self.plugin_manager.LOADED_PLUGINS:
            module = self.plugin_manager.LOADED_PLUGINS[args.command]
            module.loader(reptor=self, **self._config.get("cli")).run()
        else:
            # This is called when the user uses python -m reptor or any other way
            # but provides no arguments at all
            self._print_title()
