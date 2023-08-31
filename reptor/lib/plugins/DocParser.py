import pathlib
import typing

# Todo: Because we are not using the docs anymore, we should refactor this and rename this


class PluginDocs:
    _overwrites = None

    name: str = ""
    author: str = ""
    version: str = ""
    website: str = ""
    license: str = ""
    tags: list = []
    summary: str = ""
    category: str = ""

    path: pathlib.Path = None  # type: ignore

    def set_overwrites_plugin(self, plugin):
        self._overwrites = plugin

    def get_overwritten_plugin(self):
        return self._overwrites


class DocParser:
    @staticmethod
    def parse(meta_dictionary: typing.Dict) -> PluginDocs:
        plugin_docs = PluginDocs()
        plugin_docs.author = meta_dictionary.get("author", "")
        plugin_docs.version = meta_dictionary.get("version", "")
        plugin_docs.website = meta_dictionary.get("website", "")
        plugin_docs.license = meta_dictionary.get("license", "")
        plugin_docs.tags = meta_dictionary.get("tags", [])
        plugin_docs.summary = meta_dictionary.get("summary", "")

        return plugin_docs
