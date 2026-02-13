import json
import subprocess
import time

import pytest


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

    def test_update_finding(self, projects_api):  # noqa: F811
        update_finding = projects_api.get_findings()[0]

        title = str(time.time())
        finding = {
            "status": "in-progress",
            "data": {
                "title": title,
            },
        }

        p = subprocess.Popen(
            ["reptor", "finding", "--update", update_finding.id],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        p.communicate(input=json.dumps([finding, finding]).encode())
        assert p.returncode != 0  # Multiple findings cannot be updated

        p = subprocess.Popen(
            ["reptor", "finding", "--update", update_finding.id],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        p.communicate(input=json.dumps(finding).encode())
        assert p.returncode == 0
        updated_finding = projects_api.get_finding(update_finding.id)
        assert updated_finding.data.title == title
        assert updated_finding.data.summary == update_finding.data.summary
