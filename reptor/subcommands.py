from collections import OrderedDict

SUBCOMMANDS_GROUPS = OrderedDict(
    {
        "core": ("Core", list()),
        "projects": ("Projects & Templates", list()),
        "uploads": ("Uploads", list()),
        "tools": ("Tools", list()),
        "importers": ("Importers", list()),
        "utils": ("Utils", list()),
        "other": ("Other", list()),
        "plugins": ("User Plugins", list()),
    }
)
