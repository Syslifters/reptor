import json

import pytest
import tomli_w

from reptor.lib.reptor import Reptor

from ..Finding import Finding


class TestFinding:
    finding_json = """{
	"status": "in-progress",
	"data": {
		"cvss": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N",
		"title": "Reflected XSS",
		"summary": "We detected a reflected XSS vulnerability.\n\n**XSS targets**\n\n* https://example.com/alert(1)\n* https://example.com/q=alert(1)\n",
		"references": [
			"https://owasp.org/www-community/attacks/xss/"
		],
		"description": "",
		"recommendation": "HTML encode user-supplied inputs.",
		"affected_components": [
			"https://example.com/alert(1)",
			"https://example.com/q=alert(1)"
		]
	}
}
"""
    finding_toml = tomli_w.dumps(json.loads(finding_json, strict=False))

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reptor = Reptor()
        self.finding = Finding(reptor=self.reptor)

    def test_read_invalid_finding(self):
        with pytest.raises(ValueError):
            list(self.finding._read_findings(content="invalid"))

    def test_read_finding_with_invalid_field(self):
        invalid_finding = json.loads(self.finding_json, strict=False)
        invalid_finding["data"]["title"] = 1
        with pytest.raises(ValueError):
            list(self.finding._read_findings(content=json.dumps(invalid_finding)))

    def test_read_toml_finding(self):
        finding_content = list(self.finding._read_findings(content=self.finding_toml))[
            0
        ]
        assert isinstance(finding_content, dict)
        assert finding_content["data"]["title"] == "Reflected XSS"
        assert finding_content["data"]["summary"].startswith(
            "We detected a reflected XSS vulnerability."
        )

    def test_read_json_finding(self):
        finding_content = list(self.finding._read_findings(content=self.finding_json))[
            0
        ]
        assert isinstance(finding_content, dict)
        assert finding_content["data"]["title"] == "Reflected XSS"
        assert finding_content["data"]["summary"].startswith(
            "We detected a reflected XSS vulnerability."
        )

    def test_read_multiple_json_findings(self):
        findings = f"[{self.finding_json}, {self.finding_json}, {self.finding_json}]"
        finding_content = list(self.finding._read_findings(content=findings))
        assert len(finding_content) == 3

        finding_content = finding_content[0]
        assert isinstance(finding_content, dict)
        assert finding_content["data"]["title"] == "Reflected XSS"
        assert finding_content["data"]["summary"].startswith(
            "We detected a reflected XSS vulnerability."
        )
