import subprocess
import time

import pytest

from reptor.plugins.core.Conf.tests.conftest import (
    get_note,
    private_uploads_id,
    private_notes_api
)


@pytest.mark.integration
class TestIntegrationNote(object):
    def test_notes_upload_without_notetitle(self):
        # Upload content to "Uploads"
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--private"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        out, err = p.communicate(note_content)
        assert p.returncode == 0

        # Check if content was added to "Uploads"
        note = get_note("Uploads", None, private=True)
        assert note is not None
        assert note_content.decode() in note["text"]

    def test_notes_upload_with_notetitle(self, private_uploads_id):
        note_content = str(time.time()).encode()
        # Upload to note with notetitle
        p = subprocess.Popen(
            ["reptor", "note", "--private", "--notetitle", note_content.decode()],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Check if content was added to note with notetitle
        note = get_note(note_content.decode(), private_uploads_id, private=True)
        assert note is not None
        assert note_content.decode() in note["text"]

    def test_locked_notes(self, private_notes_api, private_uploads_id):
        # Lock "Uploads" note via notes_api
        private_notes_api._do_lock(private_uploads_id)

        # Upload content to "Uploads" (should fail, because locked)
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--private"],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 2

        # Make sure content was not added to "Uploads"
        note = get_note("Uploads", None, private=True)
        assert note is not None
        assert note_content.decode() not in note["text"]

        # Upload content to "Uploads" (should succeed, because forced)
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--private", "--force"],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Make sure content was not added to "Uploads"
        note = get_note("Uploads", None, private=True)
        assert note is not None
        assert note_content.decode() in note["text"]
