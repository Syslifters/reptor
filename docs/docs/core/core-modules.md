
## Introduction

These plugins are the foundation of the reptor CLI. If you are unhappy with some of the functionality you can also overwrite these.

## Global Arguments

The following list of arguments is available in every plugin (core, community, user):

| Argument | Description |
| ---|---|
|--help | Shows the help information to reptor or a plugin |
|--verbose / -v| More output |
|--debug | Lots of output |
|--server / -s | Endpoint Server overwrites config |
|--token / -t | Endpoint Token overwrites config |
|--project-id  / -p | Project ID overwrites config |
|--personal-note | Writes notes into the user's notes |
|--force-unlock / -f | Force unlock notes and sections |
|--insecure | Disables SSL verification (Useful for self-hosted instances) |
|--n | Specify Notename |
|--no-timestamp / -nt | Removes the timestamp inside the note when it was written |

***Note:*** When you write your own plugins you can always access any of these via `kwargs.get("NAME")` in the constructor of a plugin class. Don't forget to call super().

An example from the Plugins plugin:
```python
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ...SNIP...
        self.verbose = kwargs.get("verbose")
```

::: reptor.plugins.core.Conf.Conf

::: reptor.plugins.core.File.File

::: reptor.plugins.core.Importers.Importers

::: reptor.plugins.core.Note.Note

::: reptor.plugins.core.Plugins.Plugins

::: reptor.plugins.core.Projects.Projects

::: reptor.plugins.core.Templates.Templates

::: reptor.plugins.core.Translate.Translate
