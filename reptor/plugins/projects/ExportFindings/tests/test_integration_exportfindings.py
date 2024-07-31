import json
import subprocess

import pytest
import tomli
import yaml

from reptor.plugins.core.Conf.tests.conftest import get_note, projects_api


@pytest.mark.integration
class TestIntegrationExportFinding(object):
    def test_export_findings(self, projects_api):
        p = subprocess.Popen(
            ["reptor", "exportfindings", "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        assert p.returncode == 0
        json_export = json.loads(out)

        p = subprocess.Popen(
            ["reptor", "exportfindings", "--format", "toml"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        assert p.returncode == 0
        toml_export = tomli.loads(out.decode()).get("findings")  # TOML wraps in a dict

        p = subprocess.Popen(
            ["reptor", "exportfindings", "--format", "yaml"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        assert p.returncode == 0
        yaml_export = yaml.safe_load(out.decode())

        assert json_export == toml_export == yaml_export

        p = subprocess.Popen(
            ["reptor", "exportfindings", "--format", "json", "--upload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        assert p.returncode == 0

        note = get_note("Uploads", None)
        note_last_line = note["text"].splitlines()[-1]  # type: ignore
        assert f"[{projects_api.project.name}.json]" in note_last_line
