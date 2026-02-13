import os
import subprocess
from pathlib import Path

import pytest

from test_helpers import get_note


@pytest.mark.integration
class TestIntegrationFile(object):
    def test_upload_file(self):
        archive_path = Path(os.path.dirname(__file__)) / "data/archive.7z"

        # Without filename
        p = subprocess.Popen(
            ["reptor", "file", archive_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        assert p.returncode == 0

        note = get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]
        assert "[archive.7z]" in note_last_line

        # With filename
        fn = "myarchive.7z"
        p = subprocess.Popen(
            ["reptor", "file", "-fn", fn, archive_path],
            stdout=subprocess.PIPE,
        )
        p.communicate()
        assert p.returncode == 0

        note = get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]
        assert fn in note_last_line

    def test_upload_file_no_link(self):
        archive_path = Path(os.path.dirname(__file__)) / "data/archive.7z"

        # Get initial note state
        note_before = get_note("Uploads", None)
        initial_text = note_before["text"] if note_before else ""

        # Upload file with --no-link flag
        fn = "no_link_archive.7z"
        p = subprocess.Popen(
            ["reptor", "file", "--no-link", "-fn", fn, archive_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, err = p.communicate()
        assert p.returncode == 0
        
        # Verify successful upload message in output
        output = err.decode()
        assert "File uploaded:" in output

        # Verify that no markdown link was added to the note
        note_after = get_note("Uploads", None)
        if note_after:
            # Note should either not exist or have the same text as before
            assert note_after["text"] == initial_text, \
                "Note text should not change when using --no-link flag"
