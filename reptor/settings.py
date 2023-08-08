import pathlib

BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent

PERSONAL_SYSREPTOR_HOME: pathlib.Path = pathlib.Path.home() / ".sysreptor"
PERSONAL_CONFIG_FILE: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "config.yaml"

PLUGIN_DIRS: pathlib.Path = BASE_DIR / "plugins"
PLUGIN_DIRS_CORE: pathlib.Path = PLUGIN_DIRS / "core"
PLUGIN_DIRS_OFFICIAL: pathlib.Path = PLUGIN_DIRS / "syslifters"
PLUGIN_DIRS_COMMUNITY: pathlib.Path = PLUGIN_DIRS / "community"
PLUGIN_DIRS_IMPORTERS: pathlib.Path = PLUGIN_DIRS / "importers"
PLUGIN_DIRS_EXPORTERS: pathlib.Path = PLUGIN_DIRS / "exporters"
PLUGIN_DIRS_USER: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "plugins"

PLUGIN_TEMPLATES_DIR_NAME: str = "templates"

PLUGIN_TOOLBASE_TEMPLATE_FOLDER: pathlib.Path = BASE_DIR / "templates" / "Toolbase"

LOG_FOLDER: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "logs"

NEWLINE = "\n"

USER_AGENT = "reptor CLI v0.1.0"  # TODO dynamic version


# Django Related Setup
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "libraries": {
                "md": "reptor.utils.templatetags.md",
            },
        }
    },
]

DEBUG = True
INSTALLED_APPS = []
LOGGING_CONFIG = []
LOGGING = []
FORCE_SCRIPT_NAME = ""
