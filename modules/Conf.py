import settings

from core.modules.ConfBase import ConfBase
from core.console import reptor_console

from utils.table import make_table


class Conf(ConfBase):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: core, config

    Short Help:
    Interact with reptor configuration

    Description:
    Offers you a way to write a config file for reptor,
    allows you to quickly see the configuration without touching
    the config file
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_show = kwargs.get("show")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        config_parser = parser.add_mutually_exclusive_group()
        config_parser.add_argument(
            "--show", help="Shows current connection settings", action="store_true"
        )

    def _show_config(self):
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

    def run(self):
        if self.arg_show:
            self._show_config()
        else:
            self.config.get_config_from_user()


loader = Conf
