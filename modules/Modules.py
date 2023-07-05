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

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        project_parser = parser.add_argument_group()
        project_parser.add_argument(
            "--search", help="Search for term", action="store", default=None
        )

    def _list(self):
        table = make_table(["Name", "Short Help", "Author", "Version", "Tags"])

        # Todo: Adjust with once community and private modules are respected
        for tool in settings.SUBCOMMANDS_GROUPS[ToolBase][1]:
            table.add_row(
                tool.name,
                tool.short_help,
                tool.author,
                tool.version,
                ",".join(tool.tags),
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
