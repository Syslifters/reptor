import pathlib
import typing


class PluginDocs:
    TYPE_CORE = "CORE"
    TYPE_COMMUNITY = "COMMUNITY"
    TYPE_PRIVATE = "PRIVATE"

    _type: typing.Literal["CORE", "COMMUNITY", "PRIVATE"] = TYPE_CORE
    _overwrites = None

    name: str = ""
    author: str = ""
    version: str = ""
    website: str = ""
    license: str = ""
    tags: list = []
    summary: str = ""

    path: pathlib.Path = None  # type: ignore

    def is_community(self) -> bool:
        return self._type == self.TYPE_COMMUNITY

    def is_core(self) -> bool:
        return self._type == self.TYPE_CORE

    def is_private(self) -> bool:
        return self._type == self.TYPE_PRIVATE

    def set_community(self):
        self._type = self.TYPE_COMMUNITY

    def set_core(self):
        self._type = self.TYPE_CORE

    def set_private(self):
        self._type = self.TYPE_PRIVATE

    @property
    def space_label(self) -> str:
        if self.is_private():
            return self.TYPE_PRIVATE.capitalize()
        if self.is_core():
            return self.TYPE_CORE.capitalize()
        if self.is_community():
            return self.TYPE_COMMUNITY.capitalize()

        return ""

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
