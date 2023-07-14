import reptor.subcommands as subcommands
from reptor.lib.plugins.Base import Base
from reptor.lib.importers.BaseImporter import BaseImporter
from reptor.lib.console import reptor_console

from reptor.utils.table import make_table


class Importers(Base):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: core, import, findings

    Short Help:
    Shows available finding template importers

    Description:
    Use this module to list importers.

    Search for importers based on tags or name

    Create a new importer from a template for the community
    or yourself.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_search = kwargs.get("search")
        self.arg_new_module = kwargs.get("new")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        project_parser = parser.add_argument_group()
        project_parser.add_argument(
            "--search", help="Search for term", action="store", default=None
        )
        project_parser.add_argument(
            "--new", help="Create a new module", action="store_true", default=False
        )

    def _list(self, importers):
        table = make_table(["Name", "Short Help"])

        for item in importers:
            table.add_row(
                f"{item.name}",
                f"{item.short_help}",
            )

        reptor_console.print(table)

    def _search(self, importers):
        """Searches modules"""
        self.reptor.console.print(f"\nSearching for: [red]{self.arg_search}[/red]\n")
        results = list()
        for item in importers:
            if self.arg_search in item.tags:
                results.append(item)
                continue

            if self.arg_search in item.name:
                results.append(item)
                continue

        self._list(results)

    def _create_new_importer(self):
        ...

    def run(self):
        if self.arg_search:
            self._search(subcommands.SUBCOMMANDS_GROUPS[BaseImporter][1])
        elif self.arg_new_module:
            self._create_new_importer()
        else:
            self._list(subcommands.SUBCOMMANDS_GROUPS[BaseImporter][1])


loader = Importers
