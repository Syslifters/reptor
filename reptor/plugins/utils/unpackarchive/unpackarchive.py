import argparse
import json
import os
import tarfile
import tempfile
from pathlib import Path
from shutil import copytree
from typing import Any
from io import FileIO

import tomlkit
import tomlkit.items

from reptor.lib.plugins.Base import Base


def to_toml(data: Any):
    if isinstance(data, dict):
        table = tomlkit.table()
        keys_prepend = [
            "title",
            "cvss",
            "severity",
            "summary",
            "impact",
            "description",
            "recommendation",
        ]
        keys_append = ["report_data", "findings", "project_type", "translations"]

        ordered_keys = list(data.keys())
        for k in keys_prepend + keys_append:
            if k in ordered_keys:
                ordered_keys.remove(k)
        for k in reversed(keys_prepend):
            if k in data:
                ordered_keys.insert(0, k)
        for k in keys_append:
            if k in data:
                ordered_keys.append(k)

        for k in ordered_keys:
            if data[k] is not None:
                table.append(k, to_toml(data[k]))
        return table
    elif isinstance(data, list):
        array = (
            tomlkit.aot()
            if (len(data) > 0 and isinstance(data[0], dict))
            else tomlkit.items.Array(
                value=[], trivia=tomlkit.items.Trivia(), multiline=True
            )
        )
        for v in data:
            if v is not None:
                array.append(to_toml(v))
        return array
    elif isinstance(data, bool):
        return tomlkit.items.Bool(data, trivia=tomlkit.items.Trivia())
    elif isinstance(data, int):
        return tomlkit.items.Integer(data, trivia=tomlkit.items.Trivia(), raw=str(data))
    elif isinstance(data, float):
        return tomlkit.items.Float(data, trivia=tomlkit.items.Trivia(), raw=str(data))
    elif isinstance(data, str):
        if "\n" in data:
            if data[0] != "\n":
                data = "\n" + data
            if data[-1] != "\n":
                data += "\n"
            return tomlkit.string(data, multiline=True)
        else:
            return tomlkit.string(data)
    # elif data is None:
    #    # TOML does not support null values
    #    return None
    else:
        raise Exception(f"Unhandled type: {type(data)}")


class UnpackArchive(Base):
    meta = {
        "name": "UnpackArchive",
        "summary": "Unpack .tar.gz exported archives",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files: list[FileIO] = kwargs.get("files", [])
        self.output = kwargs.get("output") or "./unpacked_archive"
        self.format = kwargs.get("format") or "toml"

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)

        parser.add_argument("files", nargs="+", type=argparse.FileType("rb"))
        parser.add_argument("-o", "--output")
        parser.add_argument("-f", "--format", choices=["json", "toml"], default="toml")

    def run(self):
        with tempfile.TemporaryDirectory() as tempdir:
            for file in self.files:
                with tarfile.open(fileobj=file, mode="r:gz") as tar:
                    tar.extractall(tempdir)
                for path_json in Path(tempdir).glob("*.json"):
                    if not path_json.is_file():
                        continue
                    data_dict = json.loads(path_json.read_text())
                    if self.format == "json":
                        data_output = json.dumps(data_dict, indent=2)
                    elif self.format == "toml":
                        data_output = tomlkit.dumps(to_toml(data_dict))
                    path_output = path_json.with_suffix(f".{self.format}")
                    path_output.write_text(data_output)
                    if path_output != path_json:
                        path_json.unlink()

            self.output = os.path.abspath(self.output)
            copytree(src=tempdir, dst=self.output, dirs_exist_ok=True)
            self.success(f"Unpacked files to {self.output}")


loader = UnpackArchive
