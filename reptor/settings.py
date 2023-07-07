import pathlib


from collections import OrderedDict
from reptor.lib.modules.ToolBase import ToolBase
from reptor.lib.modules.ConfBase import ConfBase
from reptor.lib.modules.UploadBase import UploadBase
from reptor.lib.importers.BaseImporter import BaseImporter


BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent

PERSONAL_SYSREPTOR_HOME: pathlib.Path = pathlib.Path.home() / ".sysreptor"
PERSONAL_CONFIG_FILE: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "config.yaml"

MODULE_DIRS: pathlib.Path = BASE_DIR / "modules"
MODULE_DIRS_CORE: pathlib.Path = MODULE_DIRS / "core"
MODULE_DIRS_OFFICIAL: pathlib.Path = MODULE_DIRS / "syslifters"
MODULE_DIRS_COMMUNITY: pathlib.Path = MODULE_DIRS / "community"
MODULE_DIRS_IMPORTERS: pathlib.Path = MODULE_DIRS / "importers"
MODULE_DIRS_EXPORTERS: pathlib.Path = MODULE_DIRS / "exporters"
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
        BaseImporter: ("finding templates importers", list()),
    }
)

# Django Related Setup
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
    },
]

INSTALLED_APPS = []
LOGGING_CONFIG = []
LOGGING = []
FORCE_SCRIPT_NAME = ""
