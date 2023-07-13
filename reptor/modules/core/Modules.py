import os
import shutil

from reptor import settings, subcommands
from reptor.lib.console import reptor_console
from reptor.lib.modules.Base import Base
from reptor.lib.modules.ToolBase import ToolBase
from reptor.utils.table import make_table


class Modules(Base):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: core

    Short Help:
    Allows module management & development

    Description:
    Use this module to list your modules.

    Search for modules based on tags, name or author

    Create a new module from a template for the community
    or yourself.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = kwargs.get("search")
        self.new_module_name = kwargs.get("new_module_name")
        self.copy_module_name = kwargs.get("copy_module_name")
        self.verbose = kwargs.get("verbose")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)

        action_group = parser.add_mutually_exclusive_group()
        action_group.title = 'action_group'
        action_group.add_argument(
            "-search", "--search",
            metavar='SEARCHTERM',
            action='store',
            dest='search',
            const='',
            nargs='?',
            help="Search for term"
        )
        action_group.add_argument(
            "-new", "--new",
            metavar="PLUGINNAME",
            nargs='?',
            dest='new_module_name',
            const='',
            help="Create a new module"
        )
        action_group.add_argument(
            "-copy", "--copy",
            metavar="PLUGINNAME",
            action='store',
            dest='copy_module_name',
            help="Copy module to home directory"
        )

    def _list(self, modules):
        if self.verbose:
            table = make_table(
                [
                    "Name",
                    "Short Help",
                    "Space",
                    "Overwrites",
                    "Author",
                    "Version",
                    "Tags",
                ]
            )
        else:
            table = make_table(
                [
                    "Name",
                    "Short Help",
                    "Tags",
                ]
            )

        reptor_console.print(
            "Module Colors: [blue]Core[/blue], [green]Community[/green], [magenta]Private[/magenta], [red]Overwrites other module[/red] "
        )

        for tool in modules:
            color = "blue"
            if tool.is_community():
                color = "green"
            elif tool.is_private():
                color = "magenta"

            tool_name = f"[{color}]{tool.name}[/{color}]"

            overwritten_module = tool.get_overwritten_module()
            overwrites_name = ""
            if overwritten_module:
                overwrites_name = f"[red]{overwritten_module.name}({overwritten_module.space_label})[/red]"
                tool_name = f"[red]{tool.name}({tool.space_label})\nOverwrites: {overwritten_module.space_label}[/red]"
                color = "red"

            if self.verbose:
                table.add_row(
                    f"[{color}]{tool.name}[/{color}]",
                    f"[{color}]{tool.short_help}[/{color}]",
                    f"[{color}]{tool.space_label}[/{color}]",
                    overwrites_name,
                    f"[{color}]{tool.author}[/{color}]",
                    f"[{color}]{tool.version}[/{color}]",
                    f"[{color}]{','.join(tool.tags)}[/{color}]",
                )
            else:
                table.add_row(
                    f"{tool_name}",
                    f"[{color}]{tool.short_help}[/{color}]",
                    f"[{color}]{','.join(tool.tags)}[/{color}]",
                )

        reptor_console.print(table)

    def _search(self):
        """Searches modules"""
        if self.search:
            self.reptor.console.print(
                f"\nSearching for: [red]{self.search}[/red]\n")
            results = list()
            for module in subcommands.SUBCOMMANDS_GROUPS[ToolBase][1]:
                if self.search in module.tags:
                    results.append(module)
                    continue

                if self.search in module.name:
                    results.append(module)
                    continue
        else:
            results = subcommands.SUBCOMMANDS_GROUPS[ToolBase][1]

        self._list(results)

    def _create_new_module(self):
        """Goes through a few questions to generate a new Module.

        The user must at least answer the module Name.

        It should always be a directory based module, because of templates.

        The user can then go on and develop their own module.
        """

        # Todo: Finalise this to make it as easy as possible for new modules to be created by anyone
        # think Django's manage.py startapp or npm init

        introduction = """
        Please answer the following questions.

        Based on the answer we will create a raw module for you to work on.

        You will find the new module in your ~/.sysrepter/modules folder.
        Once you are happy with it you should offer it as a community module!

        Let's get started
        """

        self.reptor.console.print(introduction)

        if self.new_module_name:
            module_name = self.new_module_name.strip().split(" ")[0]
            print(f"Module Name: {module_name}")
        else:
            module_name = (
                input("Module Name (No spaces, try to use the tool name): ")
            ).strip().split(" ")[0]

        module_name.strip().split(" ")[0]

        author = input("Author Name: ")[:25]
        tags = input("Tags (only first: 5 Tags), i.e owasp,web,scanner: ").split(",")[
            :5
        ]

        tool_based = input("Is it based on a tool output? [N,y]:")[
            :1].lower() == "y"

    def _copy_module(self, dest=settings.MODULE_DIRS_USER):
        # Check if module exists and get its path
        try:
            plugin_path = os.path.dirname(
                settings.LOADED_MODULES[self.copy_module_name].__file__)
            plugin_dirname = os.path.basename(plugin_path)
        except KeyError:
            raise ValueError(
                f"Plugin '{self.copy_module_name}' does not exist.")
        
        # Copy module
        dest = os.path.join(dest, plugin_dirname)
        shutil.copytree(plugin_path, dest)


    def run(self):
        if self.new_module_name is not None:
            self._create_new_module()
        elif self.copy_module_name is not None:
            self._copy_module()
        else:
            self._search()
            # self._list(subcommands.SUBCOMMANDS_GROUPS[ToolBase][1])


loader = Modules
