import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api


@pytest.mark.integration
class TestIntegrationNikto(object):
    def test_nikto_notes(self, notes_api):
        input_path = Path(os.path.dirname(__file__)) / "data/nikto-multidae.xml"

        p = subprocess.Popen(
            ["reptor", "nikto", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=input_path.read_bytes())
        p.wait()
        assert p.returncode == 0

        note = notes_api.get_note_by_title(
            "nikto", parent_notename="Uploads"
        )
        note_lines = note.text.splitlines()
        lines = [
            "| IP | 127.0.0.1 |",
            "| Issues Items | 151 |",
            "| /includes/ | GET |  Directory indexing found. | None |"
        ]
        assert all([line in note_lines for line in lines])
