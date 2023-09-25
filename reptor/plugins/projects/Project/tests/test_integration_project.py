import json
import os
import subprocess

import pytest

from reptor.api.NotesAPI import NotesAPI
from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.lib.reptor import Reptor


@pytest.mark.integration
class TestIntegrationProject(object):
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["cli"] = {"personal_note": False}
        self.notes_api = NotesAPI(reptor=self.reptor)
        self.projects_api = ProjectsAPI(reptor=self.reptor)
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

    def test_render_project(self):
        projects_len = len(self.projects_api.get_projects())
        p = subprocess.Popen(
            [
                "reptor",
                "project",
                "--render",
                "--upload",
                "--design",
                "54c67723-f380-46aa-aa46-ced789fbccb6",
            ],
        )
        p.wait()
        assert p.returncode == 0

        note = self.get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]  # type: ignore
        assert f"[{self.projects_api.project.name}.pdf]" in note_last_line

        # --design duplicates project; check if cleaned up
        assert projects_len == len(self.projects_api.get_projects())

    def test_export_tar_gz(self):
        fname = "myproject.tar.gz"
        try:
            os.remove(fname)
        except OSError:
            pass
        assert not os.path.isfile(fname)

        p = subprocess.Popen(
            ["reptor", "project", "--export", "tar.gz", "-o", fname],
        )
        p.wait()
        assert p.returncode == 0

        assert os.path.isfile(fname)
        assert os.path.getsize(fname) > 0
        try:
            os.remove(fname)  # Cleanup
        except OSError:
            pass

    def test_export_json(self):
        p = subprocess.Popen(
            ["reptor", "project", "--export", "json", "-o", "-"],
            stdout=subprocess.PIPE,
        )
        p.wait()
        output, _ = p.communicate()

        assert p.returncode == 0
        json.loads(output)  # Test if we can load json
