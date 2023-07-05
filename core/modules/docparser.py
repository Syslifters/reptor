from inspect import cleandoc
import re


class ModuleDocs:
    name: str = ""
    author: str = ""
    version: str = ""
    website: str = ""
    license: str = ""
    tags: list = []
    short_help: str = ""
    description: str = ""


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
