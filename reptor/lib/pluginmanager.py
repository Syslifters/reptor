import importlib
import os
import pathlib
import sys
import typing
from pathlib import Path

import reptor.settings as settings
import reptor.subcommands as subcommands
from reptor.lib.plugins.PluginMeta import PluginMeta


class PluginManager:
    """The  PluginManager is responsible for loading all plugins and making
    them available to reptor.
    """

    _plugin_paths: typing.List = list()

    LOADED_PLUGINS: typing.Dict = dict()

    _reptor: typing.Any

    def __init__(self, reptor) -> None:
        self._reptor = reptor

    def run_loading_sequence(self):
        self._reptor.logger.info("Loading plugins...")
        self._load_modules()

    def is_loaded(self, plugin_name: str) -> bool:
        """Checks if a plugin is loaded

        Args:
            plugin_name (str): Plugin Name

        Returns:
            bool: True if found, False if not
        """
        if plugin_name in self.LOADED_PLUGINS.keys():
            return True
        return False

    def unload(self, plugin_name: str) -> bool:
        """Unloads a plugin by its name

        Args:
            plugin_name (str): Plugin Name

        Returns:
             bool: True if unloaded, otherwise False
        """
        if self.is_loaded(plugin_name):
            del self.LOADED_PLUGINS[plugin_name]
            return True
        return False

    def get_plugin_by_name(self, plugin_name: str):
        """Returns a plugin by its name, if it exists
        otherwise return is None

        Args:
            plugin_name (str): Plugin Name
        """
        if self.is_loaded(plugin_name):
            return self.LOADED_PLUGINS[plugin_name]
        return None

    def _load_plugin_from_path(self, directory: pathlib.Path):
        """Loads a File and Folder based Modules from the ./modules folder in reptor

        Returns:
            typing.List: Holds absolute paths to each Module file
        """
        self._reptor.logger.debug(f"Loading Modules from folder: {directory}")
        plugin_paths = list()
        for modules_path in directory.glob("*"):
            if "__pycache__" in modules_path.name:
                continue
            if modules_path.is_dir():
                for modules_file in modules_path.glob("*.py"):
                    plugin_paths.append(str(modules_file))

        self._plugin_paths += plugin_paths
        self._reptor.logger.debug(f"Found Plugin Paths: {plugin_paths}")

    def _load_modules(self):
        """Loads the core modules for reptor to function"""
        for plugin_path in settings.PLUGIN_IMPORT_DIRS:
            self._load_plugin_from_path(plugin_path)

    def load_plugins(self):
        """Loads each plugin from _plugin_paths

        Returns:
            typing.Dict: Dictionary holding each plugin meta information
        """

        # Be careful here: We are working technically with python modules, but
        # in reptor we call our different implementations
        # for various tools: plugins

        for plugin_path in self._plugin_paths:
            spec = importlib.util.spec_from_file_location(  # type: ignore
                "module.name", plugin_path
            )
            module = importlib.util.module_from_spec(spec)  # type: ignore

            sys.modules["module.name"] = module
            spec.loader.exec_module(module)

            # Check if the Module is Valid
            if not hasattr(module, "loader"):
                continue

            # Configure metadata
            plugin_meta = PluginMeta(module.loader.meta)
            plugin_meta.name = module.loader.__name__.lower()
            plugin_meta.path = plugin_path

            # Check what type of module it is and mark it as such
            if str(settings.PLUGIN_DIRS_USER) in plugin_path:
                plugin_meta.category = "private"
            else:
                plugin_meta.category = os.path.basename(plugin_path)

            # Add it to the correct commands group
            dir_name = Path(os.path.dirname(module.__file__)).parent.name
            subcommands_idx = (
                dir_name if dir_name in subcommands.SUBCOMMANDS_GROUPS else "other"
            )

            # check if the module is already in the list,
            # if so a later loaded module (e.g. private plugin from home dir)
            # needs to overwrite it
            for dirname, group in subcommands.SUBCOMMANDS_GROUPS.items():
                for index, existing_module in enumerate(group[1]):
                    if plugin_meta.name == existing_module.name:
                        plugin_meta.set_overwrites_plugin(existing_module)
                        subcommands.SUBCOMMANDS_GROUPS[dirname][1].pop(index)

            # add the module data to the end
            subcommands.SUBCOMMANDS_GROUPS[subcommands_idx][1].append(plugin_meta)

            # because it is a dictionary, an overwritten module is automatically overwritten
            self.LOADED_PLUGINS[plugin_meta.name] = module

        empty_groups = list()
        for group_name, group in subcommands.SUBCOMMANDS_GROUPS.items():
            if not group[1]:
                empty_groups.append(group_name)
                continue
            group[1].sort(key=lambda p: p.name)
        for empty_group in empty_groups:
            subcommands.SUBCOMMANDS_GROUPS.pop(empty_group)

        self._reptor.logger.debug(f"Loaded Plugins are: {self.LOADED_PLUGINS}")
