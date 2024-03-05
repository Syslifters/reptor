import io
import json
import os
import pathlib
import subprocess
import tarfile

import pytest
import yaml
from reptor.plugins.core.Conf.tests.conftest import templates_api


class TestIntegrationTemplate(object):
    @pytest.mark.integration
    @pytest.mark.parametrize(
        "input_file",
        ["template_1.json", "template_2.json", "template_1.toml", "template_2.toml"],
    )
    def test_upload_finding_template(self, input_file, templates_api):
        # Delete the templates if already exist
        for title in [
            "SQL Injection (SQLi)",
            "Session management weaknesses",
            "My Title",
        ]:
            for id in set([t.id for t in templates_api.search(title)]):
                templates_api.delete_template(id)

        input_path = pathlib.Path(os.path.dirname(__file__)) / f"data/{input_file}"
        p = subprocess.Popen(
            ["reptor", "template", "--upload"],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, output = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0
        output_lines = output.decode().splitlines()
        new_ids = [o.split()[-1] for o in output_lines[0:-1] if "Uploaded" in o]
        for new_id in new_ids:
            templates_api.delete_template(new_id)
        assert "Successfully uploaded" in output_lines[-1]

    def test_template_export_archive(self):
        p = subprocess.Popen(
            ["reptor", "template", "--search", "XE", "--export", "json"],
            stdout=subprocess.PIPE,
        )
        templates, _ = p.communicate()
        templates = json.loads(templates.decode())
        assert p.returncode == 0
        ids = [template["id"] for template in templates]

        p = subprocess.Popen(
            [
                "reptor",
                "template",
                "--search",
                "XE",
                "--export",
                "tar.gz",
                "--output",
                "-",
            ],
            stdout=subprocess.PIPE,
        )
        archive, _ = p.communicate()
        archive_io = io.BytesIO(archive)
        with tarfile.open(fileobj=archive_io, mode="r:gz") as tar:
            assert all(f"{id}.json" in list(tar.getnames()) for id in ids)
            assert len(tar.getmembers()) == len(ids)

    def test_template_export(self):
        input_path = pathlib.Path(os.path.dirname(__file__)) / f"data/template_1.json"
        p = subprocess.Popen(
            ["reptor", "template", "--upload"],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, output = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0

        p = subprocess.Popen(
            ["reptor", "template", "--list", "--export", "json"],
            stdout=subprocess.PIPE,
        )
        templates, _ = p.communicate()
        templates = json.loads(templates.decode())
        assert p.returncode == 0
        assert len(templates) > 0

        p = subprocess.Popen(
            ["reptor", "template", "--search", "SQL", "--export", "json"],
            stdout=subprocess.PIPE,
        )
        sql_templates, _ = p.communicate()
        sql_templates = json.loads(sql_templates.decode())
        assert p.returncode == 0
        assert len(templates) > len(sql_templates) > 0
        sql_summary = sql_templates[0]["translations"][0]["data"]["summary"]

        p = subprocess.Popen(
            ["reptor", "template", "--search", "SQL", "--export", "plain"],
            stdout=subprocess.PIPE,
        )
        sql_templates, _ = p.communicate()
        sql_templates = sql_templates.decode()
        assert p.returncode == 0
        assert sql_summary in sql_templates

        p = subprocess.Popen(
            ["reptor", "template", "--search", "SQL", "--export", "yaml"],
            stdout=subprocess.PIPE,
        )
        sql_templates, _ = p.communicate()
        sql_templates = yaml.safe_load(sql_templates.decode())
        assert p.returncode == 0
        assert len(templates) > len(sql_templates) > 0
