import json
import os
import subprocess
import time
from pathlib import Path

import pytest

from reptor.api.NotesAPI import NotesAPI
from reptor.lib.reptor import Reptor


@pytest.mark.integration
class TestIntegrationFile(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["cli"] = {"personal_note": False}
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
            ["reptor", "note", "--list", "--json"],
            stdout=subprocess.PIPE,
        )
        notes, _ = p.communicate()
        notes = json.loads(notes.decode())
        p.wait()
        assert p.returncode == 0
        return notes

    def get_note(self, name, parent, notes=None):
        if notes is None:
            notes = self.get_notes()
        for note in notes:
            if note["title"] == name and note["parent"] == parent:
                return note

    def test_upload_file(self):
        archive_path = Path(os.path.dirname(__file__)) / "data/archive.7z"

        # Without filename
        p = subprocess.Popen(
            ["reptor", "file", archive_path],
            stdout=subprocess.PIPE,
        )
        p.wait()
        assert p.returncode == 0

        note = self.get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]
        assert "[archive.7z]" in note_last_line

        # With filename
        fn = "myarchive.7z"
        p = subprocess.Popen(
            ["reptor", "file", "-fn", fn, archive_path],
            stdout=subprocess.PIPE,
        )
        p.wait()
        assert p.returncode == 0

        note = self.get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]
        assert fn in note_last_line

