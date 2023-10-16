import argparse
import logging
import signal
import sys
import traceback

import django
from django.conf import settings as django_settings

import reptor.settings as settings
import reptor.subcommands as subcommands
from reptor.api.manager import APIManager
from reptor.lib.conf import Config
from reptor.lib.console import Console, reptor_console
from reptor.lib.logger import ReptorAdapter, reptor_logger
from reptor.lib.pluginmanager import PluginManager
from reptor.lib.plugins.PluginMeta import PluginMeta
from reptor.utils.django_tags import setup_django_tags
from reptor.utils.markdown import convert_markdown_to_console

root_logger = logging.getLogger("root")


def signal_handler(sig, frame):
    reptor_console.print("[yellow]You pressed Ctrl+C![/yellow]")
    sys.exit(0)


class Reptor:
    """The reptor class is the main App.

    It is responsible for the correct loading of plugins via the PluginManager,
    enabling global arguments and forwarding any plugin calls to the correct
    plugin.

    Attributes:
        plugin_manager: AcAPIManagercess any plugins
        logger: Log to the logger
        console: Write to console via print
        api: Access the API via APIManager

    """

    _config: Config
    _parser: argparse.ArgumentParser
    _sub_parsers: argparse._SubParsersAction
    plugin_manager: PluginManager

    logger: ReptorAdapter = reptor_logger
    console: Console = reptor_console
    _api: APIManager

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Reptor, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        signal.signal(signal.SIGINT, signal_handler)

        # Load the config
        self._config = Config()
        self._config.load_config()

        # Setup Django tags
        setup_django_tags()

        self.plugin_manager = PluginManager(self)

        if self.get_config().get_log_file():
            self.logger.add_file_log()

    def get_config(self) -> Config:
        """Use this to access the current config

        Returns:
            Config: Current Configuration
        """
        return self._config

    def get_logger(self) -> ReptorAdapter:
        """Returns the active logger. Use this for logging

        Returns:
            ReptorAdapter: _description_
        """
        return self.logger

    def get_plugin_manager(self) -> PluginManager:
        """Returns the PluginManager with all loaded plugins.

        Returns:
            PluginManager: _description_
        """
        return self.plugin_manager

    def get_active_project_id(self) -> str:
        """Always returns the active project id, either from config
        or from the CLI overwrite. If no project id is found,
        then it returns an emptry string.

        Returns:
            str: Project ID
        """
        if self.get_config().get_cli_overwrite().get("project_id", ""):
            return self.get_config().get_cli_overwrite().get("project_id", "")
        if self.get_config().get_project_id():
            return self.get_config().get_project_id()
        return ""

    @property
    def api(self) -> APIManager:
        if not hasattr(self, "_api") or not self._api:
            self._api = APIManager(reptor=self)
        return self._api

    def _create_parsers(self):
        """Creates the description in the help and the parsers to be used

        Returns:
            parser,subparsers: ArgumentParser and SubParser
        """
        # Argument parser description
        description = ""
        for (
            _,
            short_help_group_meta,
        ) in subcommands.SUBCOMMANDS_GROUPS.items():
            description += f"\n{short_help_group_meta[0]}:\n"

            item: PluginMeta
            for item in short_help_group_meta[1]:
                description += f" {item.name:<21} {item.summary}{settings.NEWLINE}"

        # Argument parser
        main_description = """
            Examples:
                reptor conf
                echo "Upload this!" | reptor note
                reptor file data/*
                cat sslyze.json | reptor sslyze --json --push-findings
                cat nmap.xml | reptor nmap --xml --upload
"""
        self._parser = argparse.ArgumentParser(
            prog="reptor",
            description=main_description.strip(),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        self._sub_parsers = self._parser.add_subparsers(
            dest="command", description=description, help=argparse.SUPPRESS
        )

    def _dynamically_add_plugin_options(self):
        """
        Calls add_arguments on each plugin that is loaded and provides
        the subparser as well as the plugin file path
        """
        # Dynamically add plugin options
        for name, plugin in self.plugin_manager.LOADED_PLUGINS.items():
            plugin.subparser = self._sub_parsers.add_parser(
                name,
                description=plugin.loader.meta.get("summary", ""),
                formatter_class=argparse.RawTextHelpFormatter,
            )
            plugin_filepath = plugin.__file__
            self.logger.debug(
                f"Adding arguments for {name} with filepath {plugin_filepath}"
            )
            plugin.loader.add_arguments(
                plugin.subparser, plugin_filepath=plugin_filepath
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
            "-k",
            "--insecure",
            help="do not verify server certificate",
            action="store_true",
        )
        config_parser.add_argument("-p", "--project-id", help="SysReptor project ID")
        config_parser.add_argument(
            "--private-note", help="add notes to private notes", action="store_true"
        )
        config_parser.add_argument(
            "-f",
            "--force-unlock",
            help="force unlock notes",
            action="store_true",
        )

    def _configure_global_arguments(self):
        """Enables the parameters
        - debug
        - verbose
        - insecure
        - no-timestamp
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
        self._parser.add_argument("-n", "--notetitle")
        self._parser.add_argument(
            "--no-timestamp",
            help="do not prepend timestamp to note",
            action="store_true",
        )

        self._parser.add_argument("--file", help="Local file to read")
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
        if "-v" in sys.argv or "--verbose" in sys.argv or "-verbose" in sys.argv:
            reptor_logger.logger.setLevel(logging.INFO)
            root_logger.setLevel(logging.INFO)
        if "--debug" in sys.argv or "-debug" in sys.argv:
            reptor_logger.logger.setLevel(logging.DEBUG)
            root_logger.setLevel(logging.DEBUG)

        self.plugin_manager.run_loading_sequence()

        self.plugin_manager.load_plugins()

        django_settings.configure(settings, DEBUG=True)
        django.setup()
        self._create_parsers()

        self._dynamically_add_plugin_options()

        # Static plugin options
        self._add_config_parse_options()

        self._configure_global_arguments()
        args = self._parse_main_arguments_with_subparser()

        # Configure the API
        self._api = APIManager(reptor=self)

        # Subcommands
        if args.command in self.plugin_manager.LOADED_PLUGINS:
            try:
                plugin = self.plugin_manager.LOADED_PLUGINS[args.command]
                self.logger.debug(f"Loading Plugin: {plugin.__name__}")
                plugin.loader(reptor=self, **self._config.get("cli")).run()
            except Exception as e:
                self.logger.debug(traceback.format_exc())
                self.logger.fail(e)
                exit(2)
        else:
            # This is called when the user uses python -m reptor or any other way
            # but provides no arguments at all
            print(self._parser.format_help())
