# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Name:         Conf
# Purpose:      Show configuration or set configuration
# Author:
# Created:      2022-07-18
# ---------------------------------------------------------

from reptor.lib.plugins.ConfBase import ConfBase

from reptor.utils.table import make_table


class Conf(ConfBase):
    """
    Offers you a way to write a config file for reptor,
    allows you to quickly see the configuration without touching
    the config file
    """

    meta = {"name": "Config", "summary": "Shows config and sets config"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_show = kwargs.get("show")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        config_parser = parser.add_mutually_exclusive_group()
        config_parser.add_argument(
            "--show", help="Shows current connection settings", action="store_true"
        )

    def _show_config(self):
        self.display("Configuration Overview")

        table = make_table(["Setting", "Value"])

        table.add_row("Server", self.reptor.get_config().get_server())

        project_id = self.reptor.get_config().get_project_id()
        table.add_row("Project ID", project_id or "Writing globally.")

        self.console.print(table)

    def run(self):
        if self.arg_show:
            self._show_config()
        else:
            self.reptor.get_config().get_config_from_user()


loader = Conf
