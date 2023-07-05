import argparse
import importlib
import pathlib
import sys
import typing

import logging

from inspect import cleandoc

import settings
from .interfaces.reptor import ReptorProtocol

from core.conf import Config
from core.logger import reptor_logger
from utils.string_operations import truncate


root_logger = logging.getLogger("root")

# Todo:
# - Respect Community setting in Help Output (Community modules should only be shown when community is enabled)
# - Refactor Global and Configuration arguments
# - Refactor Output


class Reptor(ReptorProtocol):
    _config: Config
    _module_paths: typing.Any = list()
    _loaded_modules: dict = dict()
    _parser: argparse.ArgumentParser
    _sub_parsers: argparse._SubParsersAction

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Reptor, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._load_config()
        self.logger = reptor_logger

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

    def _load_module_from_path(self, directory: pathlib.Path):
        """Loads a File and Folder based Modules from the ./modules folder in reptor

        Returns:
            typing.List: Holds absolute paths to each Module file
        """
        self.logger.debug(f"Loading Modules from folder: {directory}")
        module_paths = list()
        for modules_path in directory.glob("*"):
            if "__pycache__" not in modules_path.name:
                if modules_path.is_dir():
                    module_main_file = modules_path / f"{modules_path.name}.py"
                    if module_main_file.is_file():
                        module_paths.append(str(module_main_file))
                else:
                    module_paths.append(str(modules_path))

        self._module_paths += module_paths

        self.logger.debug(f"Found Module Paths: {module_paths}")

    def _load_system_modules(self):
        """Loads the official modules of syslifters"""
        self._load_module_from_path(settings.MODULE_DIRS)

    def _load_community_modules(self):
        """If the user enabled community modules, these are loaded AFTER
        the system modules. Hence overwriting the system modules
        """
        self._load_module_from_path(settings.MODULE_DIRS_COMMUNITY)

    def _load_user_modules(self):
        """Finally the user can have their own "private" modules or
        overwrite any of the official or community modules.
        """
        self._load_module_from_path(settings.MODULE_DIRS_USER)

    def _run_module_loading_sequence(self):
        """The module loading hierachy is as followed
        System Modules -> Community Modules -> User Modules
        This allows the User to overwrite any Community Modules
        and Community Modules can overwrite System Modules
        """
        self.logger.info("Loading modules...")
        self._load_system_modules()
        if self._config.get("community", False):
            self._load_community_modules()
        self._load_user_modules()

    def _import_modules(self):
        """Loads each module

        Returns:
            typing.Dict: Dictionary holding each module name
        """

        for module in self._module_paths:
            spec = importlib.util.spec_from_file_location("module.name", module)  # type: ignore

            module = importlib.util.module_from_spec(spec)  # type: ignore
            sys.modules["module.name"] = module
            spec.loader.exec_module(module)

            # Add some metadata
            if not hasattr(module, "loader"):
                continue
            module.name = module.loader.__name__.lower()
            module.description = cleandoc(module.loader.__doc__)
            module.short_help = f"{module.name}{max(1,(15-len(module.name)))*' '}{truncate(module.description.split(settings.NEWLINE)[0], length=50)}"

            # Add short_help to tool help message
            if module.loader.__base__ in settings.SUBCOMMANDS_GROUPS:
                settings.SUBCOMMANDS_GROUPS[module.loader.__base__][1].append(
                    module.short_help
                )
            else:
                settings.SUBCOMMANDS_GROUPS["other"][1].append(module.short_help)

            self._loaded_modules[module.name] = module

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
        ) in settings.SUBCOMMANDS_GROUPS.items():
            description += f"\n{short_help_group_meta[0]}:\n"
            description += f"{settings.NEWLINE.join(short_help_group_meta[1])}\n"

        # Argument parser
        self._parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        self._sub_parsers = self._parser.add_subparsers(
            dest="command", description=description, help=argparse.SUPPRESS
        )

    def _dynamically_add_module_options(self):
        # Dynamically add module options
        for name, module in self._loaded_modules.items():
            module.subparser = self._sub_parsers.add_parser(
                name,
                description=module.description,
                formatter_class=argparse.RawTextHelpFormatter,
            )
            module.loader.add_arguments(module.subparser)

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
        for k in ["server", "project_id", "session_id", "insecure"]:
            config.set(k, args_dict.get(k) or config.get(k, ""))
        # Add cli options to config/cli
        config.set("cli", args_dict)

        self.logger.debug(f"Parsed args: {args}")
        return args

    def run(self) -> None:
        """The run method actually starts the cli application"""
        # Todo: Refactor the order when the parsers are available. Otherwise
        # with the current direction we don't have --debug and -verbose output
        # until we hit self._parse_main_arguments_with_subparser()
        self.logger.success("Reptor is starting...")

        # Todo: remove current hack for debug and verbose logging
        if "-v" in sys.argv or "--verbose" in sys.argv:
            reptor_logger.logger.setLevel(logging.INFO)
            root_logger.setLevel(logging.INFO)
        if "--debug" in sys.argv:
            reptor_logger.logger.setLevel(logging.DEBUG)
            root_logger.setLevel(logging.DEBUG)

        self._run_module_loading_sequence()

        self._import_modules()

        self._create_parsers()

        self._dynamically_add_module_options()

        # Static module options
        self._add_config_parse_options()

        self._configure_global_arguments()
        args = self._parse_main_arguments_with_subparser()

        # Subcommands
        if args.command in self._loaded_modules:
            module = self._loaded_modules[args.command]
            module.loader(reptor=self, **self._config.get("cli")).run()
