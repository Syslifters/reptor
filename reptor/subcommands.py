from collections import OrderedDict

from reptor.lib.importers.BaseImporter import BaseImporter
from reptor.lib.plugins.ConfBase import ConfBase
from reptor.lib.plugins.ToolBase import ToolBase
from reptor.lib.plugins.UploadBase import UploadBase

SUBCOMMANDS_GROUPS = OrderedDict(
    {
        ConfBase: ("configuration", list()),
        UploadBase: ("upload evidences", list()),
        ToolBase: ("tool output processing", list()),
        "other": ("other", list()),
        BaseImporter: ("finding templates importers", list()),
    }
)
