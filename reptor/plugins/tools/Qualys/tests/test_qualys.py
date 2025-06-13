import os
from pathlib import Path

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Note import NoteTemplate

from ..Qualys import Qualys


class TestQualys(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Qualys.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.qualys = Qualys()

    def _load_xml_data(self, filename):
        self.qualys.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.xml")
        with open(filepath, "r") as f:
            self.qualys.raw_input = f.read()

    def test_parse(self):
        # WAS
        self._load_xml_data("webapp_scan")
        self.qualys.parse()
        assert len(self.qualys.parsed_input) == 18

        self.qualys.raw_input = [self.qualys.raw_input, self.qualys.raw_input]
        self.qualys.parse()
        assert len(self.qualys.parsed_input) == 36

        # VULN
        self._load_xml_data("vuln_scan")
        self.qualys.parse()
        assert len(self.qualys.parsed_input) == 2

    def test_parse_with_severity_filter(self):
        # WAS
        self._load_xml_data("webapp_scan")
        self.qualys.severity_filter = {"critical"}
        self.qualys.parse()
        p = self.qualys.parsed_input
        assert isinstance(p, list)
        assert len(p) == 7

        # VULN
        self._load_xml_data("vuln_scan")
        self.qualys.severity_filter = {"critical"}
        self.qualys.parse()
        p = self.qualys.parsed_input
        assert isinstance(p, list)
        assert len(p) == 0

    def test_parse_with_qid_filter(self):
        # WAS
        self._load_xml_data("webapp_scan")
        self.qualys.included_plugins = {"150158"}
        self.qualys.parse()
        p = self.qualys.parsed_input
        assert isinstance(p, list)
        assert all(f["QID"] == "150158" for f in p)

        self.qualys.included_plugins = {}
        self.qualys.excluded_plugins = {"150158"}
        self.qualys.parse()
        p = self.qualys.parsed_input
        assert isinstance(p, list)
        assert not any(f["QID"] == "150158" for f in p)

        # VULN
        self._load_xml_data("vuln_scan")
        self.qualys.included_plugins = {"86247"}
        self.qualys.parse()
        p = self.qualys.parsed_input
        assert isinstance(p, list)
        assert all(f["QID"] == "86247" for f in p)

        self.qualys.included_plugins = {}
        self.qualys.excluded_plugins = {"86247"}
        self.qualys.parse()
        p = self.qualys.parsed_input
        assert isinstance(p, list)
        assert not any(f["QID"] == "86247" for f in p)

    def test_preprocess_for_template(self):
        # WAS
        self._load_xml_data("webapp_scan")
        self.qualys.parse()
        p = self.qualys.preprocess_for_template()
        assert len(p) == 13
        assert isinstance(p[0]["affected_components"], list)
        assert isinstance(p[0]["URLS"], list)
        assert isinstance(p[0]["PARAMS"], list)
        assert isinstance(p[0]["ACCESS_PATHS"], list)

        # VULN
        self._load_xml_data("vuln_scan")
        self.qualys.parse()
        p = self.qualys.preprocess_for_template()
        assert len(p) == 2
        assert isinstance(p[0]["affected_components"], list)
        assert isinstance(p[0]["IPS"], list)

    def test_aggregate_by_plugin(self):
        self._load_xml_data("webapp_scan")
        self.qualys.parse()
        a = self.qualys.aggregate_by_plugin()
        assert len(a) == 13
        assert sum(len(v) for v in a) == 18
        
    def test_create_notes(self):
        # WAS
        self._load_xml_data("webapp_scan")
        self.qualys.parse()
        note = self.qualys.create_notes()
        assert isinstance(note, NoteTemplate)
        assert note.icon_emoji == "🛡️"
        assert note.title == "Qualys"
        assert note.children[0].title == "ginandjuice.shop"
        assert len(note.children[0].children) == 18

        # VULN
        self._load_xml_data("vuln_scan")
        self.qualys.parse()
        note = self.qualys.create_notes()
        assert isinstance(note, NoteTemplate)
        assert note.icon_emoji == "🛡️"
        assert note.title == "Qualys"
        assert note.children[0].title == "34.249.203.140"
        assert len(note.children[0].children) == 2

    def test_aggregate_by_target(self):
        self._load_xml_data("webapp_scan")
        self.qualys.parse()
        a = self.qualys.aggregate_by_target()
        assert len(a) == 1
        assert len(a[0]) == 18
