import json
import subprocess

import pytest

from reptor.plugins.core.Conf.tests.conftest import projects_api, get_note


@pytest.mark.integration
class TestIntegrationProjectFinding(object):
    def test_render_project(self, projects_api):
        p = subprocess.Popen(
            ["reptor", "projectfindings", "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        assert p.returncode == 0
        json.loads(out)

        p = subprocess.Popen(
            ["reptor", "projectfindings", "--format", "json", "--upload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        assert p.returncode == 0

        note = get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]  # type: ignore
        assert f"[{projects_api.project.name}.json]" in note_last_line
