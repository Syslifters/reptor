import settings
from core.modules.Base import Base
from core.modules.ToolBase import ToolBase
from core.console import reptor_console
from core.modules.docparser import ModuleDocs

from utils.table import make_table


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
            "--new", help="Create a new module", action="store", default=None
        )

    def _list(self):
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

        for tool in settings.SUBCOMMANDS_GROUPS[ToolBase][1]:
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
        ...

    def run(self):
        if self.arg_search:
            self._search()
        else:
            self._list()


loader = Modules
