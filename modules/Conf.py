import settings

from core.modules.ConfBase import ConfBase
from core.modules.ToolBase import ToolBase
from core.console import reptor_console
from core.modules.docparser import ModuleDocs

from utils.table import make_table


class Conf(ConfBase):
    """
    enter config interactively and store to file
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_list = kwargs.get("list")
        self.arg_modules = kwargs.get("modules")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        config_parser = parser.add_mutually_exclusive_group()
        config_parser.add_argument(
            "--list", help="Shows current connection settings", action="store_true"
        )

        config_parser.add_argument(
            "--modules", help="Shows current loaded modules", action="store_true"
        )

    def run(self):
        if self.arg_list:
            self.logger.display("Configuration Overview")
            table = make_table(["Setting", "Value"])

            table.add_row("Server", self.config.get_server())

            project_id = self.config.get_project_id()
            table.add_row("Project ID", project_id or "Writing globally.")

            community_enabled = "[green]Enabled[/green]"
            if not self.config.get_community_enabled():
                community_enabled = "[yellow]Disabled[/yellow]"
            table.add_row("Community Modules", community_enabled)

            reptor_console.print(table)
        elif self.arg_modules:
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
        else:
            self.config.get_config_from_user()


loader = Conf
