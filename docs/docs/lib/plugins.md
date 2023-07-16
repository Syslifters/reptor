# Introduction
Every plugin should be based on one of the following base classes.

This ensures, that they are correctly loaded into the plugin manager.

All plugins that are based on a tool and it's respective output should inherit
from ToolBase.

::: reptor.lib.plugins.Base

::: reptor.lib.plugins.ConfBase

::: reptor.lib.plugins.ToolBase

::: reptor.lib.plugins.UploadBase


# Models
If your plugin is more complex and you wish to create custom models
you can use the ModelBase.

::: reptor.lib.plugins.ModelBase