import subprocess

import pytest


@pytest.mark.integration
class TestIntegrationTranslate(object):
    def test_dry_run(self):
        p = subprocess.Popen(
            ["reptor", "translate", "--dry-run", "--to", "DE", "--debug"],
            stderr=subprocess.PIPE,
        )
        _, output = p.communicate()
        output = output.decode()
        assert p.returncode == 0

        translated_characters = 0
        for line in output.splitlines():
            if line.startswith("Translated "):
                translated_characters = int(line.split()[1])
                break
        assert translated_characters > 1000

        # Run with skip-fields
        p = subprocess.Popen(
            [
                "reptor",
                "translate",
                "--dry-run",
                "--to",
                "DE",
                "--skip-fields",
                "executive_summary",
            ],
            stderr=subprocess.PIPE,
        )
        _, output = p.communicate()
        output = output.decode()
        assert p.returncode == 0

        less_translated_characters = 0
        for line in output.splitlines():
            if line.startswith("Translated "):
                less_translated_characters = int(line.split()[1])
                break
        assert translated_characters > less_translated_characters > 1000
