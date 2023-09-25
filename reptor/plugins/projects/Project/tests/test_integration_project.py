import json
import os
import subprocess

import pytest

from reptor.plugins.core.Conf.tests.conftest import (
    get_note,
    get_notes,
    notes_api,
    projects_api,
)


@pytest.mark.integration
class TestIntegrationProject(object):
    def test_render_project(self, projects_api):
        projects_len = len(projects_api.get_projects())
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

        note = get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]  # type: ignore
        assert f"[{projects_api.project.name}.pdf]" in note_last_line

        # --design duplicates project; check if cleaned up
        assert projects_len == len(projects_api.get_projects())

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
