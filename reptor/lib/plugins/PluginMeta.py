import pathlib
import typing


class PluginMeta:
    _overwrites = None

    name: str = ""
    author: str = ""
    version: str = ""
    website: str = ""
    license: str = ""
    tags: list = []
    summary: str = ""
    category: str = ""

    path: typing.Optional[pathlib.Path] = None

    def __init__(self, meta_dictionary: typing.Dict):
        self.author = meta_dictionary.get("author", "")
        self.version = meta_dictionary.get("version", "")
        self.website = meta_dictionary.get("website", "")
        self.license = meta_dictionary.get("license", "")
        self.tags = meta_dictionary.get("tags", [])
        self.summary = meta_dictionary.get("summary", "")

    def set_overwrites_plugin(self, plugin):
        self._overwrites = plugin

    def get_overwritten_plugin(self):
        return self._overwrites
