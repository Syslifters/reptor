import json
import subprocess
import time

import pytest

from reptor.plugins.core.Conf.tests.conftest import projects_api  # noqa: F401


@pytest.mark.integration
class TestIntegrationFinding(object):
    def test_push_valid_finding(self, projects_api):  # noqa: F811
        title = str(time.time())
        reference = "https://example.com/" + title
        affected_component = "https://example.com/affected/" + title
        finding = {
            "status": "in-progress",
            "data": {
                "cvss": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N",
                "title": title,
                "inexistent-field": "should be ignored",
                "summary": "We detected a reflected XSS vülnerability.",
                "references": [reference],
                "description": "The impact was heavy.",
                "recommendation": "HTML encode user-supplied inputs.",
                "affected_components": [
                    affected_component,
                    "https://example.com/q=alert(1)",
                ],
            },
        }
        p = subprocess.Popen(
            ["reptor", "finding"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        p.communicate(input=json.dumps(finding).encode())
        assert p.returncode == 0

        findings = projects_api.get_findings()
        f = None
        for f in findings:
            if f.data.title == title:
                break

        assert f is not None
        assert f.data.title == title
        assert f.data.references == [reference]
        assert f.data.affected_components == [
            affected_component,
            "https://example.com/q=alert(1)",
        ]
        assert f.data.summary == "We detected a reflected XSS vülnerability."

    def test_push_invalid_finding(self, projects_api):  # noqa: F811
        title = str(time.time())
        finding = {
            "status": "in-progress",
            "data": {
                "cvss": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N",
                "title": title,
                "inexistent-field": "should be ignored",
                "summary": "We detected a reflected XSS vulnerability.",
                "references": [],
                "description": "The impact was heavy.",
                "recommendation": "HTML encode user-supplied inputs.",
                "affected_components": "ERROR: This should be list",
            },
        }
        p = subprocess.Popen(
            ["reptor", "finding"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        _, err = p.communicate(input=json.dumps(finding).encode())
        assert p.returncode == 2
        findings = projects_api.get_findings()
        assert title not in [f.data.title for f in findings]
        assert (
            "affected_components" in err.decode()
        )  # The errornous field should occur in error message
