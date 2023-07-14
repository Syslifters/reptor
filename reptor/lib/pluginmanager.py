import importlib
import pathlib
import sys
import typing

from inspect import cleandoc

import reptor.settings as settings
import reptor.subcommands as subcommands

from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.lib.plugins.DocParser import DocParser


class PluginManager:
    _plugin_paths: typing.List = list()

    LOADED_PLUGINS: typing.Dict = dict()

    _reptor: ReptorProtocol

    def __init__(self, reptor) -> None:
        self._reptor = reptor

    def run_loading_sequence(self):
        """The module loading hierachy is as followed
        System Modules -> Community Modules -> User Modules
        This allows the User to overwrite any Community Modules
        and Community Modules can overwrite System Modules
        """
        self._reptor.logger.info("Loading modules...")
        self._load_core_modules()
        self._load_syslifters_modules()
        if self._reptor._config.get("community", False):
            self._load_community_modules()

        self._load_importers()
        self._load_exporters()

        self._load_user_modules()

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
            elif modules_path.suffix == ".py":
                plugin_paths.append(str(modules_path))

        self._plugin_paths += plugin_paths

        self._reptor.logger.debug(f"Found Plugin Paths: {plugin_paths}")

    def _load_core_modules(self):
        """Loads the core modules for reptor to function"""
        self._load_plugin_from_path(settings.PLUGIN_DIRS_CORE)

    def _load_syslifters_modules(self):
        """Loads the official modules created by syslifters"""
        self._load_plugin_from_path(settings.PLUGIN_DIRS_OFFICIAL)

    def _load_community_modules(self):
        """If the user enabled community modules, these are loaded AFTER
        the system modules. Hence overwriting the system modules
        """
        self._load_plugin_from_path(settings.PLUGIN_DIRS_COMMUNITY)

    def _load_user_modules(self):
        """Finally the user can have their own "private" modules or
        overwrite any of the official or community modules.
        """
        self._load_plugin_from_path(settings.PLUGIN_DIRS_IMPORTERS)

    def _load_importers(self):
        """Finally the user can have their own "private" modules or
        overwrite any of the official or community modules.
        """
        self._load_plugin_from_path(settings.PLUGIN_DIRS_EXPORTERS)

    def _load_exporters(self):
        """Export Project findings to CSV or similar..."""
        ...

    def load_plugins(self):
        """Loads each plugin from _plugin_paths

        Returns:
            typing.Dict: Dictionary holding each plugin meta information
        """

        # Be careful here: We are working technically with python modules, but
        # in reptor we call our different implementations
        # for various tools: plugins

        for plugin_path in self._plugin_paths:
            spec = importlib.util.spec_from_file_location(
                "module.name", plugin_path
            )  # type: ignore

            self._reptor.logger.debug(plugin_path)

            module = importlib.util.module_from_spec(spec)  # type: ignore

            sys.modules["module.name"] = module
            spec.loader.exec_module(module)

            # Check if the Module is Valid
            if not hasattr(module, "loader"):
                continue

            # Configure metadata
            module.description = cleandoc(module.loader.__doc__)
            plugin_docs = DocParser.parse(module.description)
            plugin_docs.name = module.loader.__name__.lower()
            plugin_docs.path = plugin_path

            # Check what type of module it is and mark it as such
            if str(settings.PLUGIN_DIRS_CORE) in plugin_path:
                plugin_docs.set_core()
            if str(settings.PLUGIN_DIRS_OFFICIAL) in plugin_path:
                plugin_docs.set_core()
            if str(settings.PLUGIN_DIRS_COMMUNITY) in plugin_path:
                plugin_docs.set_community()
            if str(settings.PLUGIN_DIRS_USER) in plugin_path:
                plugin_docs.set_private()

            # Add it to the correct commands group
            if module.loader.__base__ in subcommands.SUBCOMMANDS_GROUPS:
                # check if the module is already in the list,
                # if so a later loaded module, from community or private
                # needs to overwrite it

                for index, existing_module in enumerate(
                    subcommands.SUBCOMMANDS_GROUPS[module.loader.__base__][1]
                ):
                    if existing_module.name == plugin_docs.name:
                        # we have the case of an overwrite
                        # save the overwritten module details
                        plugin_docs.set_overwrites_plugin(existing_module)

                        # remove the original item
                        subcommands.SUBCOMMANDS_GROUPS[module.loader.__base__][1].pop(
                            index
                        )
                # add the module data to the end
                subcommands.SUBCOMMANDS_GROUPS[module.loader.__base__][1].append(
                    plugin_docs
                )

            else:
                # Todo: Other section shouldn't be left out, maybe refactor logic above to easily reuse
                subcommands.SUBCOMMANDS_GROUPS["other"][1].append(plugin_docs)

            # because it is a dictionary, an overwritten module is automatically overwritten
            self.LOADED_PLUGINS[plugin_docs.name] = module
