import io
import json
import subprocess
import tarfile

import pytest
import yaml


@pytest.mark.integration
class TestIntegrationTemplate(object):
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
        p = subprocess.Popen(
            ["reptor", "template", "--export", "json"],
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
