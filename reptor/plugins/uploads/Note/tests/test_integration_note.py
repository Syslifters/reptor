import json
import subprocess
import time

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api, uploads_id, get_note


@pytest.mark.integration
class TestIntegrationNote(object):
    def test_notes_upload_without_notename(self):
        # Upload content to "Uploads"
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--personal", "--debug"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Check if content was added to "Uploads"
        note = get_note("Uploads", None)
        assert note is not None
        assert note_content.decode() in note["text"]

    def test_notes_upload_with_notename(self, uploads_id):
        note_content = str(time.time()).encode()
        # Upload to note with notename
        p = subprocess.Popen(
            ["reptor", "note", "--personal", "--notename", note_content.decode()],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Check if content was added to note with notename
        note = get_note(note_content.decode(), uploads_id)
        assert note is not None
        assert note_content.decode() in note["text"]

    def test_locked_notes(self, notes_api, uploads_id):
        # Lock "Uploads" note via notes_api
        notes_api._do_lock(uploads_id)

        # Upload content to "Uploads" (should fail, because locked)
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--personal"],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 2

        # Make sure content was not added to "Uploads"
        note = get_note("Uploads", None)
        assert note is not None
        assert note_content.decode() not in note["text"]

        # Upload content to "Uploads" (should succeed, because forced)
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--personal", "--force"],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Make sure content was not added to "Uploads"
        note = get_note("Uploads", None)
        assert note is not None
        assert note_content.decode() in note["text"]
