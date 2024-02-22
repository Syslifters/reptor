import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import get_note


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
