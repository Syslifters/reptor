import pathlib
import shutil

import reptor.settings as settings
import reptor.subcommands as subcommands
from reptor.lib.plugins.Base import Base
from reptor.utils.table import make_table


class Plugins(Base):
    """
    Use this plugin to list your plugins.

    Search for plugins based on tags, name or author

    Create a new plugin from a template for the community
    or yourself.

    # Arguments

    * --search    Allows you to search for a specific plugin by name and tag
    * --copy PLUGINNAME      Copies a plugin to your local folder for development
    * --new PLUGINNAME  Creates a new plugin based off a template and your input
    * --verbose   Provides more information about a plugin

    # Developer Notes
    You can modify the `_list` method to change the output for search as
    well as the default output.
    """

    meta = {
        "name": "Plugins",
        "summary": "Allows plugin management & development",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search = kwargs.get("search")
        self.new_plugin_name = kwargs.get("new_plugin_name")
        self.copy_plugin_name = kwargs.get("copy_plugin_name")
        self.verbose = kwargs.get("verbose")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)

        action_group = parser.add_mutually_exclusive_group()
        action_group.title = "action_group"
        action_group.add_argument(
            "--search",
            metavar="SEARCHTERM",
            action="store",
            dest="search",
            const="",
            nargs="?",
            help="Search for term",
        )
        action_group.add_argument(
            "--new",
            metavar="PLUGINNAME",
            nargs="?",
            dest="new_plugin_name",
            const="",
            help="Create a new plugin",
        )
        action_group.add_argument(
            "--copy",
            metavar="PLUGINNAME",
            action="store",
            dest="copy_plugin_name",
            help="Copy plugin to home directory",
        )

    def _list(self, plugins):
        if self.verbose:
            table = make_table(
                [
                    "Name",
                    "Short Help",
                    "Space",
                    "Overwrites",
                    "Author",
                    "Version",
                    "Tags",
                ]
            )
        else:
            table = make_table(
                [
                    "Name",
                    "Short Help",
                    "Tags",
                ]
            )

        for tool in plugins:
            color = "blue"
            tool_name = f"[{color}]{tool.name}[/{color}]"

            overwritten_plugin = tool.get_overwritten_plugin()
            overwrites_name = ""
            if overwritten_plugin:
                overwrites_name = f"[red]{overwritten_plugin.name}({overwritten_plugin.category})[/red]"
                tool_name = f"[red]{tool.name}({tool.category})\nOverwrites: {overwritten_plugin.category}[/red]"
                color = "red"

            if self.verbose:
                table.add_row(
                    f"[{color}]{tool.name}[/{color}]",
                    f"[{color}]{tool.summary}[/{color}]",
                    f"[{color}]{tool.category}[/{color}]",
                    overwrites_name,
                    f"[{color}]{tool.author}[/{color}]",
                    f"[{color}]{tool.version}[/{color}]",
                    f"[{color}]{','.join(tool.tags)}[/{color}]",
                )
            else:
                table.add_row(
                    f"{tool_name}",
                    f"[{color}]{tool.summary}[/{color}]",
                    f"[{color}]{','.join(tool.tags)}[/{color}]",
                )

        self.console.print(table)

    def _search(self):
        """Searches plugins"""
        plugins = list()
        for _, group_plugins in subcommands.SUBCOMMANDS_GROUPS.items():
            plugins.extend(group_plugins[1])
        if self.search:
            self.console.print(f"\nSearching for: [red]{self.search}[/red]\n")
            results = list()
            for plugin in plugins:
                if self.search in plugin.tags:
                    results.append(plugin)
                    continue

                if self.search in plugin.name:
                    results.append(plugin)
                    continue
        else:
            results = plugins

        self._list(results)

    def _create_new_plugin(self):
        """Goes through a few questions to generate a new plugin.

        The user must at least answer the plugin Name.

        It should always be a directory based plugin, because of templates.

        The user can then go on and develop their own plugin.
        """

        # Todo: Finalise this to make it as easy as possible for new plugins to be created by anyone
        # think Django's manage.py startapp or npm init

        introduction = """
        Please answer the following questions.

        Based on the answers we will create a raw plugin for you to work on.
        You will find the new plugin in your ~/.sysrepter/plugins folder.

        Let's get started...
        """

        self.reptor.console.print(introduction)

        if self.new_plugin_name:
            plugin_name = self.new_plugin_name.strip().split(" ")[0]
            print(f"plugin Name: {plugin_name}")
        else:
            plugin_name = (
                (input("plugin Name (No spaces, try to use the tool name): "))
                .strip()
                .split(" ")[0]
            )

        plugin_name.strip().split(" ")[0]

        author = input("Author Name: ")[:25] or "Unknown"
        tags = input("Tags (only first: 5 Tags), i.e owasp,web,scanner: ").split(",")[
            :5
        ]

        # Create the folder
        new_plugin_folder = pathlib.Path(settings.PLUGIN_DIRS_USER / plugin_name)

        try:
            new_plugin_folder.mkdir(parents=True)
        except FileExistsError:
            self.highlight(
                "A plugin with this name already exists in your home directory."
            )
            overwrite = input("Do you want to continue? [N/y]: ") or "n"

            if overwrite[0].lower() != "y":
                raise AssertionError("Aborting...")

        shutil.copytree(
            settings.PLUGIN_TOOLBASE_TEMPLATE_FOLDER,
            new_plugin_folder / "",
            dirs_exist_ok=True,
        )

        # Now rename some stuff and replace some placeholders
        new_plugin_file = new_plugin_folder / f"{plugin_name.capitalize()}.py"
        pathlib.Path(new_plugin_folder / "Toolbase.py").rename(new_plugin_file)

        with open(new_plugin_file, "r+") as f:
            contents = f.read()
            contents = contents.replace("MYMODULENAME", plugin_name.capitalize())
            contents = contents.replace("AUTHOR_NAME", author)
            contents = contents.replace("TAGS_LIST", ",".join(tags))

            f.seek(0)
            f.write(contents)
            f.truncate()

        self.log.success(f"New plugin created. Happy coding! ({new_plugin_folder})")

    def _copy_plugin(self, dest=settings.PLUGIN_DIRS_USER):
        # Check if plugin exists and get its path
        try:
            plugin = pathlib.Path(
                self.reptor.plugin_manager.LOADED_PLUGINS[
                    self.copy_plugin_name
                ].__file__
            )
        except KeyError:
            raise ValueError(f"Plugin '{self.copy_plugin_name}' does not exist.")

        # Copy plugin

        dest = dest / plugin.parent.name
        self.log.display(f'Trying to copy "{plugin.parent}" to "{dest}"')
        shutil.copytree(plugin.parent, dest)
        self.log.success(f"Copied successfully. ({dest})")

    def run(self):
        if self.new_plugin_name is not None:
            self._create_new_plugin()
        elif self.copy_plugin_name is not None:
            self._copy_plugin()
        else:
            self._search()


loader = Plugins
