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

    @pytest.mark.parametrize(
        "score,severity,vector",
        [
            (9.2, "Critical", "CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N"),
            (9.2, "Critical", "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/CR:M/MAV:N/MAT:P"),
            (8.4, "High", "CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N"),
            (4.2, "Medium", "CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L/E:U/RC:U"),
            (6.0, "Medium", "CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L/E:U/RC:U"),
            (2.4, "Low", "CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N"),
            (5.8, "Medium", "AV:L/AC:M/Au:M/C:N/I:C/A:C"),
        ],
    )
    def test_cvss_version_exports(self, score, severity, vector):
        finding = {
            "status": "in-progress",
            "data": {
                "title": "Finding Title CVSS",
                "cvss": vector,
            },
        }
        p = subprocess.Popen(
            ["reptor", "finding"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        out, err = p.communicate(input=json.dumps(finding).encode())
        assert p.returncode == 0

        p = subprocess.Popen(
            ["reptor", "exportfindings", "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = p.communicate()
        results = json.loads(out)
        for result in results:
            if result.get("title") == "Finding Title CVSS":
                assert result["cvss__score"] == str(score)
                assert result["cvss__severity"] == severity
                assert result["cvss__vector"] == vector
                break
        assert p.returncode == 0