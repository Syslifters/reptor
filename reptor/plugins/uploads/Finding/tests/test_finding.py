import json

import pytest
import toml

from reptor.lib.reptor import Reptor
from reptor.models.Finding import Finding as FindingModel

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
    finding_toml = toml.dumps(json.loads(finding_json, strict=False))

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reptor = Reptor()
        self.finding = Finding(reptor=self.reptor)

    def test_read_invalid_finding(self):
        with pytest.raises(ValueError):
            self.finding._read_finding(content="invalid")

    def test_read_toml_finding(self):
        finding_content = self.finding._read_finding(content=self.finding_toml)
        assert isinstance(finding_content, FindingModel)
        assert finding_content.data.title.value == "Reflected XSS"
        assert finding_content.data.summary.value.startswith(
            "We detected a reflected XSS vulnerability."
        )

    def test_read_json_finding(self):
        finding_content = self.finding._read_finding(content=self.finding_json)
        assert isinstance(finding_content, FindingModel)
        assert finding_content.data.title.value == "Reflected XSS"
        assert finding_content.data.summary.value.startswith(
            "We detected a reflected XSS vulnerability."
        )
