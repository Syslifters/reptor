from reptor import subcommands
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
        self.arg_search = kwargs.get("search")
        self.arg_new_module = kwargs.get("new")
        self.arg_verbose = kwargs.get("verbose")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        project_parser = parser.add_argument_group()
        project_parser.add_argument(
            "--search", help="Search for term", action="store", default=None
        )
        project_parser.add_argument(
            "--new", help="Create a new module", action="store_true", default=False
        )

    def _list(self, modules):
        if self.arg_verbose:
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

            if self.arg_verbose:
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
        self.reptor.console.print(
            f"\nSearching for: [red]{self.arg_search}[/red]\n")
        results = list()
        for module in subcommands.SUBCOMMANDS_GROUPS[ToolBase][1]:
            if self.arg_search in module.tags:
                results.append(module)
                continue

            if self.arg_search in module.name:
                results.append(module)
                continue

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

        module_name = (
            input("Module Name (No spaces, try to use the tool name): ")
            .strip()
            .split(" ")[0]
        )

        author = input("Author Name: ")[:25]
        tags = input("Tags (only first: 5 Tags), i.e owasp,web,scanner: ").split(",")[
            :5
        ]

        tool_based = input("Is it based on a tool output? [N,y]:")[
            :1].lower() == "y"

    def run(self):
        if self.arg_search:
            self._search()
        elif self.arg_new_module:
            self._create_new_module()
        else:
            self._list(subcommands.SUBCOMMANDS_GROUPS[ToolBase][1])


loader = Modules
