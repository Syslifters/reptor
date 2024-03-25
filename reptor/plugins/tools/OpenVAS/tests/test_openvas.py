import os
from pathlib import Path

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Note import NoteTemplate

from ..OpenVAS import OpenVAS


class TestOpenVAS(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        OpenVAS.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.openvas = OpenVAS()

    def _load_xml_data(self, filename):
        self.openvas.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.xml")
        with open(filepath, "r") as f:
            self.openvas.raw_input = f.read()

    def test_parse_multi_input(self):
        self._load_xml_data("openvas")
        self.openvas.raw_input = [self.openvas.raw_input, self.openvas.raw_input]
        self.openvas.parse()
        assert len(self.openvas.parsed_input) == 72

    def test_parse_with_qod_filter(self):
        self._load_xml_data("openvas")
        self.openvas.min_qod = 50
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 5

    def test_parse_with_filter(self):
        self._load_xml_data("openvas")
        self.openvas.severity_filter = {"critical"}
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 11

    def test_preprocess_for_template(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        p = self.openvas.preprocess_for_template()
        assert len(p) == 36
        assert p[0]["affected_components"] == ["10.20.0.125"]
        assert p[0]["risk_factor"] == "critical"
        assert p[0]["oid"] == "1.3.6.1.4.1.25623.1.0.103674"
        assert p[0]["oid"] in p[0]["finding_templates"]
        assert p[0]["cvss_vector"] == "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        assert len(set([f["name"] for f in p])) == 36
        assert all(isinstance(f.get("affected_components"), list) for f in p)

    def test_aggregate_by_plugin(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        a = self.openvas.aggregate_by_plugin()
        assert len(a) == 36
        assert all([len(v) == 1 for v in a])

    def test_create_notes(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        note = self.openvas.create_notes()
        assert isinstance(note, NoteTemplate)
        assert note.icon_emoji == "🦖"
        assert note.title == "OpenVAS"
        assert note.children[0].title == "10.20.0.125"
        assert len(note.children[0].children) == 36

        # Test "get_reports_response"
        self._load_xml_data("openvas")
        assert self.openvas.raw_input is not None
        self.openvas.raw_input = f"""<get_reports_response status="200" status_text="OK">{self.openvas.raw_input}</get_reports_response>"""
        self.openvas.parse()
        note = self.openvas.create_notes()
        assert isinstance(note, NoteTemplate)
        assert note.icon_emoji == "🦖"
        assert note.title == "OpenVAS"
        assert note.children[0].title == "10.20.0.125"
        assert len(note.children[0].children) == 36

    def test_aggregate_by_target(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        a = self.openvas.aggregate_by_target()
        assert len(a) == 1
        assert len(a[0]) == 36

    def test_parse(self):
        self._load_xml_data("openvas")
        self.openvas.parse()
        p = self.openvas.parsed_input
        assert isinstance(p, list)
        assert len(p) == 36

        # Check sorting
        severity = 10
        for finding in p:
            assert finding["severity"] <= severity
            severity = finding["severity"]

        assert p[0]["target"] == "10.20.0.125"
        assert p[0]["risk_factor"] == "critical"
        assert p[0]["host"]["ip"] == "10.20.0.125"
        assert p[0]["nvt"]["oid"] == "1.3.6.1.4.1.25623.1.0.103674"
        assert p[0]["nvt"]["tags"]["cvss_base_vector"] == "AV:N/AC:L/Au:N/C:C/I:C/A:C"
        assert p[0]["nvt"]["tags"]["summary"].startswith("The Operating System (OS)")
