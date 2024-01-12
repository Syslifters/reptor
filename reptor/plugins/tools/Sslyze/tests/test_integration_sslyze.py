import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api, projects_api


@pytest.mark.integration
class TestIntegrationSslyze(object):
    def test_sslyze_note(self, notes_api):
        input_path = Path(os.path.dirname(__file__)) / "data/sslyze_v5.json"

        p = subprocess.Popen(
            ["reptor", "sslyze", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0

        note = notes_api.get_note_by_title(
            "🚩 www.example.com:443 (127.0.0.1)", parent_notetitle="Sslyze"
        )
        note_lines = note.text.splitlines()
        lines = [
            ' * <span style="color: red">SSLv2</span>',
            ' * <span style="color: green">TLS 1.2</span>',
            ' * SHA1 in certificate chain: <span style="color: green">No</span>',
            ' * Heartbleed: <span style="color: red">Yes</span>',
            ' * No Secure Renegotiation: <span style="color: red">Yes</span>',
            ' * <span style="color: orange">DHE-RSA-AES256-SHA256</span> (TLS 1.2)',
        ]
        assert all([line in note_lines for line in lines])

    def test_sslyze_findings(self, projects_api):
        nmap_output_path = Path(os.path.dirname(__file__)) / "data/sslyze_v5.json"

        p = subprocess.Popen(
            ["reptor", "sslyze", "--push-findings"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=nmap_output_path.read_bytes())
        assert p.returncode == 0

        projects_api.get_findings()
        assert "Weak TLS setup might impact encryption" in [
            f.data.title for f in projects_api.get_findings()
        ]
