import io
import json
import os
import pathlib
import subprocess
import tarfile

import pytest
import yaml


@pytest.mark.integration
class TestIntegrationTemplate(object):
    @pytest.mark.parametrize(
        "input_file",
        ["template_1.json", "template_2.json", "template_1.toml", "template_2.toml"],
    )
    def test_upload_finding_template(self, input_file, templates_api):  # noqa: F811
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

    def test_update_finding_template(self, templates_api):  # noqa: F811
        # Delete the template if already exists
        for title in ["SQL Injection (SQLi)", "Updated SQL Injection"]:
            for id in set([t.id for t in templates_api.search(title)]):
                templates_api.delete_template(id)

        # Upload a template first
        input_path = pathlib.Path(os.path.dirname(__file__)) / "data/template_1.json"
        p = subprocess.Popen(
            ["reptor", "template", "--upload"],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, output = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0
        output_lines = output.decode().splitlines()
        template_id = [o.split()[-1] for o in output_lines if "Uploaded" in o][0]

        # Modify the template
        template_data = json.loads(input_path.read_text())
        template_data["translations"][0]["data"]["title"] = "Updated SQL Injection"
        template_data["tags"].append("updated")

        # Update the template
        p = subprocess.Popen(
            ["reptor", "template", "--update", template_id],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, output = p.communicate(input=json.dumps(template_data).encode())
        assert p.returncode == 0
        output_decoded = output.decode()
        assert "Updated finding template" in output_decoded
        assert template_id in output_decoded
        assert "Successfully updated" in output_decoded

        # Verify the update
        updated_template = templates_api.get_template(template_id)
        assert updated_template.translations[0].data.title == "Updated SQL Injection"
        assert "updated" in updated_template.tags

        # Clean up
        templates_api.delete_template(template_id)

    def test_update_multiple_templates_fails(self, templates_api):  # noqa: F811
        # Delete the template if already exists
        for title in ["SQL Injection (SQLi)"]:
            for id in set([t.id for t in templates_api.search(title)]):
                templates_api.delete_template(id)

        # Upload a template first
        input_path = pathlib.Path(os.path.dirname(__file__)) / "data/template_1.json"
        p = subprocess.Popen(
            ["reptor", "template", "--upload"],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, output = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0
        output_lines = output.decode().splitlines()
        template_id = [o.split()[-1] for o in output_lines if "Uploaded" in o][0]

        # Try to update with multiple templates (create an array with 2 templates)
        template_data = json.loads(input_path.read_text())
        multiple_templates = [template_data, template_data]
        
        p = subprocess.Popen(
            ["reptor", "template", "--update", template_id],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, output = p.communicate(input=json.dumps(multiple_templates).encode())
        assert p.returncode == 0
        output_decoded = output.decode()
        assert "Only one template can be updated at a time" in output_decoded

        # Clean up
        templates_api.delete_template(template_id)

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
        input_path = pathlib.Path(os.path.dirname(__file__)) / "data/template_1.json"
        p = subprocess.Popen(
            ["reptor", "template", "--upload"],
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, _ = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0

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
