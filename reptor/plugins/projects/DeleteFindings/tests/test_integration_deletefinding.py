import json
import subprocess

import pytest


@pytest.mark.integration
class TestIntegrationDeleteFinding(object):
    def test_delete_and_push_findings(self):
        p = subprocess.Popen(
            ["reptor", "deletefindings", "--no-dry-run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.communicate()

        for i in range(3):
            finding = {
                "status": "in-progress",
                "data": {
                    "title": f"Finding Title {i}",
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

    @pytest.mark.parametrize(
        "title_contains,exclude_title_contains,expected",
        [
            ("Finding", "", ["Finding Title 0", "Finding Title 1", "Finding Title 2"]),
            ("Finding", "1", ["Finding Title 0", "Finding Title 2"]),
            ("", "2", ["Finding Title 0", "Finding Title 1"]),
            ("", "", ["Finding Title 0", "Finding Title 1", "Finding Title 2"]),
            ("1", "", ["Finding Title 1"]),
            ("1", "1", []),
            ("", "Finding", []),
        ],
    )
    def test_delete_dry_run(self, title_contains, exclude_title_contains, expected):
        p = subprocess.Popen(
            [
                "reptor",
                "deletefindings",
                "--title-contains",
                title_contains,
                "--exclude-title-contains",
                exclude_title_contains,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, output = p.communicate()
        assert p.returncode == 0
        for title in expected:
            assert title in output.decode()

    def test_delete(self):
        p = subprocess.Popen(
            [
                "reptor",
                "deletefindings",
                "--no-dry-run",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, output = p.communicate()
        assert p.returncode == 0
        for i in range(3):
            assert f"Finding Title {i}" in output.decode()
