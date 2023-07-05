import pathlib
import re
import typing

from enum import StrEnum
from inspect import cleandoc


class MODULE_TYPE(StrEnum):
    CORE = "CORE"
    COMMUNITY = "COMMUNITY"
    PRIVATE = "PRIVATE"


class ModuleDocs:
    _type: typing.Literal["CORE", "COMMUNITY", "PRIVATE"] = MODULE_TYPE.CORE
    _overwrites = None

    name: str = ""
    author: str = ""
    version: str = ""
    website: str = ""
    license: str = ""
    tags: list = []
    short_help: str = ""
    description: str = ""

    path: pathlib.Path | None = None

    def is_community(self) -> bool:
        return self._type == MODULE_TYPE.COMMUNITY

    def is_core(self) -> bool:
        return self._type == MODULE_TYPE.CORE

    def is_private(self) -> bool:
        return self._type == MODULE_TYPE.PRIVATE

    def set_community(self):
        self._type = MODULE_TYPE.COMMUNITY

    def set_core(self):
        self._type = MODULE_TYPE.CORE

    def set_private(self):
        self._type = MODULE_TYPE.PRIVATE

    @property
    def space_label(self) -> str:
        if self.is_private():
            return MODULE_TYPE.PRIVATE.capitalize()
        if self.is_core():
            return MODULE_TYPE.CORE.capitalize()
        if self.is_community():
            return MODULE_TYPE.COMMUNITY.capitalize()

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
