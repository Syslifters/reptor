import importlib
import sys
import typing

from inspect import cleandoc

import settings
from core.conf import Config

from utils.string_operations import truncate

from .interfaces.reptor import ReptorProtocol


class Reptor(ReptorProtocol):
    _config: Config

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Reptor, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._load_config()

        self._load_system_modules()

        # if config[community_modules_enabled]
        self._load_community_modules()

        self._configure_global_arguments()

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

    def _load_system_modules(self):
        """Loads a File and Folder based Modules from the ./modules folder in reptor

        Returns:
            typing.List: Holds absolute paths to each Module file
        """
        module_paths = list()
        for modules_path in settings.MODULE_DIRS.glob("*"):
            if "__pycache__" not in modules_path.name:
                if modules_path.is_dir():
                    module_main_file = modules_path / f"{modules_path.name}.py"
                    if module_main_file.is_file():
                        module_paths.append(str(module_main_file))
                else:
                    module_paths.append(str(modules_path))
        return module_paths

    def _load_community_modules(self) -> None:
        ...

    def _import_modules(self, module_paths: typing.List):
        """Loads each module

        Returns:
            typing.Dict: Dictionary holding each module name
        """
        loaded_modules = dict()
        for module in module_paths:
            spec = importlib.util.spec_from_file_location("module.name", module)
            module = importlib.util.module_from_spec(spec)
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

            loaded_modules[module.name] = module
        return loaded_modules

    def _configure_global_arguments(self) -> None:
        """Enables the parameters
        - project_id
        - verbose
        - insecure
        """
        ...

    def run(self, *args, **kwargs) -> None:
        ...
