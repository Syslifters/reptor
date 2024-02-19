import json
import os
import pathlib
import subprocess

import pytest
import yaml

from reptor.plugins.core.Conf.tests.conftest import (
    notes_api,
    projects_api,
    read_until,
    templates_api,
)


@pytest.mark.integration
class TestIntegrationNessus(object):

    def test_upload_finding_templates(self, templates_api):
        # Delete existing finding templates
        for tag in ["nessus:global", "nessus:22964"]:
            templates = templates_api.get_templates_by_tag(tag)
            for template in templates:
                templates_api.delete_template(template.id)

        # Upload finding templates
        p = subprocess.Popen(
            ["reptor", "nessus", "--upload-finding-templates"],
            stderr=subprocess.PIPE,
        )
        _, output = p.communicate()
        assert p.returncode == 0
        output_lines = output.decode().splitlines()
        assert output_lines[-1].startswith("Successfully uploaded ")
        assert "Uploaded finding template \"global\"." in output_lines
        assert "Uploaded finding template \"22964\"." in output_lines

    @pytest.mark.parametrize(
        "input_file,expected_include,expected_exclude",
        [("nessus_single_host", 1, 5), ("nessus_multi_host", 2, 10)],
    )
    def test_nessus_template_vars(self, input_file, expected_include, expected_exclude):
        input_path = pathlib.Path(os.path.dirname(__file__)) / f"data/{input_file}.xml"

        p = subprocess.Popen(
            ["reptor", "nessus", "--template-vars", "--include", "11219,25216"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        output, _ = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0
        parsed = json.loads(output)
        assert len(parsed) == expected_include

        p = subprocess.Popen(
            ["reptor", "nessus", "--template-vars", "--exclude", "11219,25216"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        output, _ = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0
        parsed = json.loads(output)
        assert len(parsed) == expected_exclude

    @pytest.mark.parametrize(
        "input_file,expected_len",
        [("nessus_single_host", 1), ("nessus_multi_host", 4)],
    )
    def test_nessus_parse(self, input_file, expected_len):
        input_path = pathlib.Path(os.path.dirname(__file__)) / f"data/{input_file}.xml"

        p = subprocess.Popen(
            ["reptor", "nessus", "--parse"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        output, _ = p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0
        parsed = json.loads(output)
        assert len(parsed) == expected_len

    def test_nessus_note(self, notes_api):
        input_path = (
            pathlib.Path(os.path.dirname(__file__)) / "data/nessus_single_host.xml"
        )

        p = subprocess.Popen(
            ["reptor", "nessus", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=input_path.read_bytes())
        assert p.returncode == 0

        note = notes_api.get_note_by_title(
            "🟢 Nessus SYN scanner", parent_notetitle="preprod.boardvantage.net"
        )
        note_lines = note.text.splitlines()
        lines = [
            "Port 443/tcp was found to be open",
            "**Severity:** Info  ",
        ]
        assert all([line in note_lines for line in lines])

    def test_nessus_findings(self, projects_api):
        nmap_output_path = (
            pathlib.Path(os.path.dirname(__file__)) / "data/nessus_single_host.xml"
        )

        p = subprocess.Popen(
            ["reptor", "nessus", "--push-findings"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=nmap_output_path.read_bytes())
        assert p.returncode == 0

        projects_api.get_findings()
        assert "Nessus SYN scanner" in [
            f.data.title for f in projects_api.get_findings()
        ]

    def test_conf(self):
        # Must be last test as it modifies the config file
        # Test interactive config
        p = subprocess.Popen(
            ["reptor", "nessus", "--conf"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
        )
        read_until(p.stdout)
        p.stdin.write(b"medium-critical\n")  # type: ignore
        p.stdin.flush()  # type: ignore

        read_until(p.stdout)
        p.stdin.write(b"1234,9876\n")  # type: ignore
        p.stdin.flush()  # type: ignore

        read_until(p.stdout)
        p.stdin.write(b"4567,5678\n")  # type: ignore
        p.stdin.flush()  # type: ignore

        read_until(p.stdout)
        p.stdin.write(b"y\n")  # type: ignore
        p.stdin.flush()  # type: ignore
        p.wait(timeout=5)

        # Assert config file was created correctly
        with open(pathlib.Path.home() / ".sysreptor/config.yaml") as f:
            config = yaml.safe_load(f)["nessus"]

        assert all(
            [s in ["medium", "high", "critical"] for s in config["severity_filter"]]
        )
        assert config["excluded_plugins"] == ["1234", "9876"]
        assert config["included_plugins"] == ["4567", "5678"]
