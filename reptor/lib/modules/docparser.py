import pathlib
import re
import typing

from inspect import cleandoc


class ModuleDocs:
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
    short_help: str = ""
    description: str = ""

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

    def set_overwrites_module(self, module):
        self._overwrites = module

    def get_overwritten_module(self):
        return self._overwrites


class DocParser:
    @staticmethod
    def parse(raw_text: str) -> ModuleDocs:
        cleaned_docs = cleandoc(raw_text)
        module_docs = ModuleDocs()
        if author := re.findall(r"Author: (.*)", cleaned_docs):
            module_docs.author = author[0]

        if version := re.findall(r"Version: (.*)", cleaned_docs):
            module_docs.version = version[0]

        if website := re.findall(r"Website: (.*)", cleaned_docs):
            module_docs.website = website[0]

        if license := re.findall(r"License: (.*)", cleaned_docs):
            module_docs.license = license[0]

        if tags := re.findall(r"Tags: (.*)", cleaned_docs):
            module_docs.tags = [tag.strip() for tag in tags[0].split(",")]

        if short_help := re.findall(r"Short Help:\n(.*)", cleaned_docs):
            module_docs.short_help = short_help[0]

        if description := re.findall(r"Description:\n((.*\n){1,10})", cleaned_docs):
            module_docs.description = description[0][0].strip()

        return module_docs
