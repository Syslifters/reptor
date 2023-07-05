import pathlib

from collections import OrderedDict
from core.modules.ToolBase import ToolBase
from core.modules.ConfBase import ConfBase
from core.modules.UploadBase import UploadBase

BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent

PERSONAL_SYSREPTOR_HOME: pathlib.Path = pathlib.Path.home() / ".sysreptor"
PERSONAL_CONFIG_FILE: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "config.yaml"

MODULE_DIRS: pathlib.Path = BASE_DIR / "modules"
MODULE_DIRS_COMMUNITY: pathlib.Path = BASE_DIR / "community"
MODULE_DIRS_USER: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "modules"

LOG_FOLDER: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "logs"

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
