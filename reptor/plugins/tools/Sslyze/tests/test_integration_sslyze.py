import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api, projects_api


@pytest.mark.integration
class TestIntegrationSslyze(object):
    def test_sslyze_note(self, notes_api):
        input_path = Path(os.path.dirname(__file__)) / "data/sslyze.json"

        p = subprocess.Popen(
            ["reptor", "sslyze", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=input_path.read_bytes())
        p.wait()
        assert p.returncode == 0

        note = notes_api.get_note_by_title("sslyze", parent_notename="Uploads")
        note_lines = note.text.splitlines()
        lines = [
            ' * <span style="color: green">TLS 1.2</span>',
            ' * SHA1 in certificate chain: <span style="color: green">No</span>',
            ' * Heartbleed: <span style="color: green">No</span>',
            ' * No Secure Renegotiation: <span style="color: green">No</span>',
            ' * <span style="color: red">DHE-RSA-AES256-SHA256</span> (TLS 1.2)',
        ]
        assert all([line in note_lines for line in lines])

    def test_sslyze_findings(self, projects_api):
        nmap_output_path = Path(os.path.dirname(__file__)) / "data/sslyze.json"

        p = subprocess.Popen(
            ["reptor", "sslyze", "--push-findings", "--debug"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=nmap_output_path.read_bytes())
        p.wait()
        assert p.returncode == 0

        projects_api.get_findings()
        assert "Weak SSL ciphers" in [f.data.title for f in projects_api.get_findings()]
