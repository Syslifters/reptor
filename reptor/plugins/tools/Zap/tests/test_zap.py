import os
from pathlib import Path

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Note import NoteTemplate

from ..Zap import Zap


class TestOwaspZap(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Zap.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.zap = Zap(reptor=self.reptor)

    def _load_xml_data(self, xml_file):
        self.zap.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{xml_file}")
        with open(filepath, "r") as f:
            self.zap.raw_input = f.read()

    def _load_json_data(self, json_file):
        self.zap.input_format = "json"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{json_file}")
        with open(filepath, "r") as f:
            self.zap.raw_input = f.read()

    def test_json_parsing(self):
        pass

    def test_xml_parsing(self):
        self._load_xml_data("zap-report.xml")
        self.zap.parse()
        assert len(self.zap.parsed_input) == 2

        assert self.zap.parsed_input[0]["host"] == "localhost"
        assert self.zap.parsed_input[0]["port"] == "443"
        assert self.zap.parsed_input[0]["ssl"] == "true"
        assert self.zap.parsed_input[0]["name"] == "https://localhost"
        assert len(self.zap.parsed_input[0]["alerts"]) == 5

        assert (
            self.zap.parsed_input[0]["alerts"][0]["name"]
            == "Application Error Disclosure"
        )
        assert self.zap.parsed_input[0]["alerts"][0]["riskcode"] == "2"
        assert self.zap.parsed_input[0]["alerts"][0]["confidence"] == "2"
        assert self.zap.parsed_input[0]["alerts"][0]["riskdesc"] == "Medium (Medium)"
        assert self.zap.parsed_input[0]["alerts"][0]["desc"].startswith(
            "This page contains an error/warning"
        )
        assert len(self.zap.parsed_input[0]["alerts"][0]["instances"]) == 34

        assert self.zap.parsed_input[1]["host"] == "localhost"
        assert self.zap.parsed_input[1]["port"] == "80"
        assert self.zap.parsed_input[1]["ssl"] == "false"
        assert self.zap.parsed_input[1]["name"] == "http://localhost"
        assert len(self.zap.parsed_input[1]["alerts"]) == 7

    def test_create_notes(self):
        self._load_xml_data("zap-report.xml")
        self.zap.parse()
        note_template = self.zap.create_notes()
        assert isinstance(note_template, NoteTemplate)

        assert len(note_template.children) == 2
        assert isinstance(note_template.children[0], NoteTemplate)
        assert note_template.children[0].title == "http://localhost (7)"
        assert isinstance(note_template.children[0].template_data, dict)
        assert "name" in note_template.children[0].template_data
        assert len(note_template.children[0].template_data["alerts"]) == 7

        assert len(note_template.children[0].children) == 7
        assert isinstance(note_template.children[0].children[0], NoteTemplate)
        assert (
            note_template.children[0].children[0].title
            == "🔴 Cross Site Scripting (Reflected)"
        )
        assert isinstance(note_template.children[0].children[0].template_data, dict)
        assert "confidencedesc" in note_template.children[0].children[0].template_data
        assert (
            note_template.children[0].children[0].template_data["confidencedesc"]
            == "Medium"
        )

    def test_formatting(self):
        self._load_xml_data("zap-report.xml")
        self.zap.format()
        assert isinstance(self.zap.formatted_input, str)
        assert "# https://localhost (5)" in self.zap.formatted_input
        assert "# http://localhost (7)" in self.zap.formatted_input

        site_details = """| Target | Information |
| :--- | :--- |
| Site | https://localhost |
| Host | localhost |
| Port | 443 |
| SSL ? |  Yes  |"""

        assert site_details in self.zap.formatted_input

        csp_issue = """| Target | Information |
| :--- | :--- |
| Risk | Medium (High) |
| Number of Affected Instances | 117 |
| CWE | [693](https://cwe.mitre.org/data/definitions/693.html) |
"""
        assert csp_issue in self.zap.formatted_input
