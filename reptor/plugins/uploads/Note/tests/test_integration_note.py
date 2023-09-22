import json
import subprocess
import time

import pytest

from reptor.api.NotesAPI import NotesAPI
from reptor.lib.reptor import Reptor


@pytest.mark.integration
class TestIntegrationNote(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["cli"] = {"personal_note": True}
        self.notes_api = NotesAPI(reptor=self.reptor)
        self.notes_api.write_note("Create Note")
        uploads_note = self.get_note("Uploads", None)
        assert uploads_note is not None
        self.uploads_id = uploads_note["id"]

        yield

        # Delete all notes via notes_api
        for note in self.get_notes():
            self.notes_api.delete_note(note["id"])

        # Assert notes are gone
        notes = self.get_notes()
        assert len(notes) == 0

    def get_notes(self):
        p = subprocess.Popen(
            ["reptor", "note", "--personal", "--list", "--json"],
            stdout=subprocess.PIPE,
        )
        p.wait()
        notes, _ = p.communicate()
        notes = json.loads(notes.decode())
        assert p.returncode == 0
        return notes

    def get_note(self, name, parent, notes=None):
        if notes is None:
            notes = self.get_notes()
        for note in notes:
            if note["title"] == name and note["parent"] == parent:
                return note

    def test_notes_upload_without_notename(self):
        # Upload content to "Uploads"
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--personal"],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Check if content was added to "Uploads"
        note = self.get_note("Uploads", None)
        assert note is not None
        assert note_content.decode() in note["text"]

    def test_notes_upload_with_notename(self):
        note_content = str(time.time()).encode()
        # Upload to note with notename
        p = subprocess.Popen(
            ["reptor", "note", "--personal", "--notename", note_content.decode()],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 0

        # Check if content was added to note with notename
        note = self.get_note(note_content.decode(), self.uploads_id)
        assert note is not None
        assert note_content.decode() in note["text"]

    def test_locked_notes(self):
        # Lock "Uploads" note via notes_api
        self.notes_api._do_lock(self.uploads_id)

        # Upload content to "Uploads" (should fail, because locked)
        note_content = str(time.time()).encode()
        p = subprocess.Popen(
            ["reptor", "note", "--personal"],
            stdin=subprocess.PIPE,
        )
        p.communicate(note_content)
        assert p.returncode == 2

        # Make sure content was not added to "Uploads"
        note = self.get_note("Uploads", None)
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
        note = self.get_note("Uploads", None)
        assert note is not None
        assert note_content.decode() in note["text"]
