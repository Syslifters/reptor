import json
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Finding import FindingRaw
from reptor.models.ProjectDesign import ProjectDesign
from reptor.models.Project import Project

from ..Sslyze import Sslyze


class TestSslyze(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Sslyze.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.sslyze = Sslyze(reptor=self.reptor)

    def _load_json_data(self):
        self.sslyze.input_format = "json"
        filepath = os.path.join(os.path.dirname(__file__), "./data/sslyze.json")
        with open(filepath, "r") as f:
            self.sslyze.raw_input = f.read()

    def test_generate_and_push_findings(self):
        # Patch API
        self.reptor.api.templates.search = Mock(return_value=[])

        self._load_json_data()
        # Assert "create_finding" is called if no findings exist
        self.sslyze.reptor.api.projects.get_findings = Mock(return_value=[])
        self.reptor.api.projects.create_finding = MagicMock()

        self.sslyze.generate_and_push_findings()
        assert self.reptor.api.projects.create_finding.called

        # Assert "create_finding" is not called if finding with same title exists
        finding_raw = FindingRaw({"data": {"title": "Weak SSL ciphers"}})
        self.reptor.api.projects.project = Project({"project_type": ""})
        self.reptor.api.project_designs.project_design = ProjectDesign()
        self.reptor.api.projects.get_findings = Mock(return_value=[finding_raw])
        self.reptor.api.projects.create_finding = MagicMock()

        self.sslyze.generate_and_push_findings()
        assert not self.sslyze.reptor.api.projects.create_finding.called

    def test_generate_findings(self):
        # Patch API
        self.reptor.api.templates.search = Mock(return_value=[])

        self._load_json_data()
        self.sslyze.generate_findings()
        assert len(self.sslyze.findings) == 1
        cipher = self.sslyze.findings[0]
        assert cipher.data.title.value == "Weak SSL ciphers"
        assert (
            cipher.data.description.value
            == 'We detected weak SSL/TLS ciphers on your server.\n**www.example.com:443 (127.0.0.1)**\n&nbsp;\n * <span style="color: red">DHE-RSA-AES256-SHA256</span> (TLS 1.2)\n * <span style="color: red">AES256-SHA256</span> (TLS 1.2)\n * <span style="color: red">ECDHE-RSA-AES256-SHA384</span> (TLS 1.2)\n * <span style="color: red">DHE-RSA-AES256-SHA</span> (TLS 1.2)\n * <span style="color: red">AES256-SHA</span> (TLS 1.2)\n * <span style="color: red">AES256-GCM-SHA384</span> (TLS 1.2)\n * <span style="color: red">DHE-RSA-AES128-SHA256</span> (TLS 1.2)\n * <span style="color: red">DHE-RSA-AES128-SHA</span> (TLS 1.2)\n * <span style="color: red">AES128-SHA</span> (TLS 1.2)\n * <span style="color: red">AES128-SHA256</span> (TLS 1.2)\n * <span style="color: red">AES128-GCM-SHA256</span> (TLS 1.2)\n * <span style="color: red">ECDHE-RSA-AES128-SHA256</span> (TLS 1.2)\n'
        )
        assert (
            cipher.data.affected_components.value[0].value
            == "www.example.com:443 (127.0.0.1)"
        )
        assert [r.value for r in cipher.data.references.value] == [
            "https://ssl-config.mozilla.org/",
            "https://ciphersuite.info/",
        ]

    def test_parse(self):
        result_dict = {"a": "b"}
        self.sslyze.raw_input = json.dumps(result_dict)
        self.sslyze.parse()
        assert self.sslyze.parsed_input == result_dict

    def test_preprocess_for_template(self):
        result = {
            "data": [
                {
                    "hostname": "www.example.com",
                    "port": "443",
                    "ip_address": "127.0.0.1",
                    "protocols": {
                        "tlsv1_2": {
                            "weak_ciphers": [
                                "DHE-RSA-AES256-SHA256",
                                "AES256-SHA256",
                                "ECDHE-RSA-AES256-SHA384",
                                "DHE-RSA-AES256-SHA",
                                "AES256-SHA",
                                "AES256-GCM-SHA384",
                                "DHE-RSA-AES128-SHA256",
                                "DHE-RSA-AES128-SHA",
                                "AES128-SHA",
                                "AES128-SHA256",
                                "AES128-GCM-SHA256",
                                "ECDHE-RSA-AES128-SHA256",
                            ]
                        }
                    },
                    "has_weak_ciphers": True,
                    "certinfo": {
                        "certificate_matches_hostname": True,
                        "has_sha1_in_certificate_chain": False,
                        "certificate_untrusted": [],
                    },
                    "vulnerabilities": {
                        "heartbleed": False,
                        "openssl_ccs": False,
                        "robot": False,
                    },
                    "has_vulnerabilities": False,
                    "misconfigurations": {
                        "compression": False,
                        "downgrade": False,
                        "client_renegotiation": False,
                        "no_secure_renegotiation": False,
                    },
                }
            ]
        }
        self._load_json_data()
        self.sslyze.parsed_input = None
        self.sslyze.parse()
        data = self.sslyze.preprocess_for_template()
        assert data == result

    def test_format(self):
        # result = """| Host | Port | Service | Version |"""
        self._load_json_data()

        # Protocols template
        protocols_result = '    * <span style="color: green">TLS 1.2</span>\n'
        self.sslyze.template = "protocols"
        self.sslyze.format()
        assert self.sslyze.formatted_input == protocols_result

        # certinfo template
        certinfo_result = """ * <span style="color: green">Certificate is trusted</span>
 * Certificate matches hostname: <span style="color: green">Yes</span>
 * SHA1 in certificate chain: <span style="color: green">No</span>
"""
        self.sslyze.template = "certinfo"
        self.sslyze.format()
        assert self.sslyze.formatted_input == certinfo_result

        # vulnerabilities template
        vulnerabilities_result = """ * Heartbleed: <span style="color: green">No</span>
 * Robot Attack: <span style="color: green">No</span>
 * OpenSSL CCS (CVE-2014-0224): <span style="color: green">No</span>
"""
        self.sslyze.template = "vulnerabilities"
        self.sslyze.format()
        assert self.sslyze.formatted_input == vulnerabilities_result

        # misconfigurations template
        misconfigurations_result = """ * Compression: <span style="color: green">No</span>
 * Downgrade Attack (no SCSV fallback): <span style="color: green">No</span>
 * No Secure Renegotiation: <span style="color: green">No</span>
 * Client Renegotiation: <span style="color: green">No</span>
"""
        self.sslyze.template = "misconfigurations"
        self.sslyze.format()
        assert self.sslyze.formatted_input == misconfigurations_result

        # weak ciphers template
        weak_ciphers_result = """ * <span style="color: red">DHE-RSA-AES256-SHA256</span> (TLS 1.2)
 * <span style="color: red">AES256-SHA256</span> (TLS 1.2)
 * <span style="color: red">ECDHE-RSA-AES256-SHA384</span> (TLS 1.2)
 * <span style="color: red">DHE-RSA-AES256-SHA</span> (TLS 1.2)
 * <span style="color: red">AES256-SHA</span> (TLS 1.2)
 * <span style="color: red">AES256-GCM-SHA384</span> (TLS 1.2)
 * <span style="color: red">DHE-RSA-AES128-SHA256</span> (TLS 1.2)
 * <span style="color: red">DHE-RSA-AES128-SHA</span> (TLS 1.2)
 * <span style="color: red">AES128-SHA</span> (TLS 1.2)
 * <span style="color: red">AES128-SHA256</span> (TLS 1.2)
 * <span style="color: red">AES128-GCM-SHA256</span> (TLS 1.2)
 * <span style="color: red">ECDHE-RSA-AES128-SHA256</span> (TLS 1.2)
"""
        self.sslyze.template = "weak_ciphers"
        self.sslyze.format()
        assert self.sslyze.formatted_input == weak_ciphers_result

        # summary template
        self.sslyze.template = "default_summary"
        self.sslyze.format()
        for content in [
            certinfo_result,
            vulnerabilities_result,
            misconfigurations_result,
            weak_ciphers_result,
            protocols_result,
        ]:
            assert content in self.sslyze.formatted_input

    def test_path_methods(self):
        plugin_path = Path(os.path.normpath(Path(os.path.dirname(__file__)) / ".."))
        template_paths = self.sslyze.get_plugin_dir_paths(
            plugin_path, "templates", skip_user_plugins=True
        )
        assert len(template_paths) == 1
        assert isinstance(template_paths[0], Path)
        assert template_paths[0] == plugin_path / "templates"

        templates = self.sslyze.get_filenames_from_paths(template_paths, "md")
        template_names = [
            "certinfo",
            "default_summary",
            "misconfigurations",
            "protocols",
            "vulnerabilities",
            "weak_ciphers",
        ]
        assert all([t in templates for t in template_names])
