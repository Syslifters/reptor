import pathlib

from collections import OrderedDict
from core.modules.ToolBase import ToolBase
from core.modules.ConfBase import ConfBase
from core.modules.UploadBase import UploadBase

BASE_DIR = pathlib.Path(__file__).parent

PERSONAL_SYSREPTOR_HOME = pathlib.Path.home() / ".sysreptor"
PERSONAL_CONFIG_FILE = PERSONAL_SYSREPTOR_HOME / "config.yaml"

MODULE_DIRS = BASE_DIR / "modules"
MODULE_DIRS_COMMUNITY = BASE_DIR / "community"
MODULE_DIRS_USER = PERSONAL_SYSREPTOR_HOME / "modules"

NEWLINE = "\n"

USER_AGENT = "reptor CLI v0.1.0"  # TODO dynamic version

SUBCOMMANDS_GROUPS = OrderedDict(
    {
        ConfBase: ("configuration", list()),
        UploadBase: ("upload", list()),
        ToolBase: ("tool output processing", list()),
        "other": ("other", list()),
    }
)


LOGGING = {}
