from collections import OrderedDict

from reptor.lib.importers.BaseImporter import BaseImporter
from reptor.lib.modules.ConfBase import ConfBase
from reptor.lib.modules.ToolBase import ToolBase
from reptor.lib.modules.UploadBase import UploadBase

SUBCOMMANDS_GROUPS = OrderedDict(
    {
        ConfBase: ("configuration", list()),
        UploadBase: ("upload", list()),
        ToolBase: ("tool output processing", list()),
        "other": ("other", list()),
        BaseImporter: ("finding templates importers", list()),
    }
)
