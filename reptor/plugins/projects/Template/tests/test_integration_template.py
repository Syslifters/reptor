import json
import subprocess

import pytest


@pytest.mark.integration
class TestIntegrationTemplate(object):
    def test_template(self):
        p = subprocess.Popen(
            ["reptor", "template", "--json"],
            stdout=subprocess.PIPE,
        )
        templates, _ = p.communicate()
        templates = json.loads(templates.decode())
        assert p.returncode == 0
        assert len(templates) > 0

        p = subprocess.Popen(
            ["reptor", "template", "--search", "SQL", "--json"],
            stdout=subprocess.PIPE,
        )
        sql_templates, _ = p.communicate()
        sql_templates = json.loads(sql_templates.decode())
        assert p.returncode == 0
        assert len(templates) > len(sql_templates) > 0
