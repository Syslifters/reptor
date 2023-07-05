import settings

from core.modules.ConfBase import ConfBase
from core.modules.ToolBase import ToolBase


class Conf(ConfBase):
    """
    enter config interactively and store to file
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list = kwargs.get("list")
        self.modules = kwargs.get("modules")

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
        if self.list:
            print(f"Connected to: {self.config.get('server')}")
            if self.config.get("project_id"):
                print(f"Using Project: {self.config.get('project_id')}")
            else:
                print("Writing globally.")
        elif self.modules:
            for tool in settings.SUBCOMMANDS_GROUPS[ToolBase][1]:
                print(tool)
        else:
            self.config.get_config_from_user()


loader = Conf
