import json
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from django.template.loader import render_to_string

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin
from reptor.models.Finding import FindingRaw
from reptor.models.Project import Project
from reptor.models.ProjectDesign import ProjectDesign

from ..Sslyze import Sslyze


class TestSslyze(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Sslyze.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.sslyze = Sslyze(reptor=self.reptor)

    def _load_json_data(self, filename):
        self.sslyze.input_format = "json"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{filename}.json")
        with open(filepath, "r") as f:
            self.sslyze.raw_input = f.read()

    def test_finding_content(self):
        context = {
            "data": [
                {
                    "hostname": "example.com",
                    "port": "443",
                    "ip_address": "127.0.0.1",
                    "vulnerabilities": {"heartbleed": True},
                    "protocols": {
                        "sslv2": {"a": "b"},
                    },
                    "certinfo": {
                        "certificate_matches_hostname": False,
                        "certificate_untrusted": ["Android", "Apple"],
                    },
                    "misconfigurations": {
                        "compression": False,
                        "downgrade": True,
                        "no_secure_renegotiation": True,
                        "accepts_client_renegotiation": False,
                    },
                    "has_vulnerabilities": True,
                    "flag_for_finding": True,
                    "has_insecure_protocols": True,
                    "has_weak_ciphers": True,
                    "has_weak_protocols": True,
                    "has_insecure_ciphers": True,
                    "has_cert_issues": True,
                    "has_misconfigurations": True,
                },
                {
                    "hostname": "www.example.com",
                    "port": "443",
                    "ip_address": "127.0.0.1",
                    "vulnerabilities": {"robot": True},
                    "protocols": {
                        "sslv3": {"a": "b"},
                        "tlsv1_1": {"weak_ciphers": []},
                    },
                    "certinfo": {
                        "certificate_matches_hostname": True,
                        "certificate_untrusted": ["Android"],
                    },
                    "misconfigurations": {
                        "compression": True,
                        "downgrade": True,
                        "no_secure_renegotiation": True,
                        "accepts_client_renegotiation": True,
                    },
                    "has_vulnerabilities": True,
                    "flag_for_finding": True,
                    "has_insecure_protocols": True,
                    "has_weak_ciphers": True,
                    "has_weak_protocols": True,
                    "has_insecure_ciphers": False,
                    "has_cert_issues": True,
                    "has_misconfigurations": True,
                },
                {
                    "hostname": "ftp.example.com",
                    "port": "443",
                    "ip_address": "127.0.0.1",
                    "vulnerabilities": {"openssl_ccs": True},
                    "protocols": {"tlsv1_2": {"weak_ciphers": []}},
                    "misconfigurations": {
                        "compression": False,
                        "downgrade": False,
                        "no_secure_renegotiation": False,
                        "accepts_client_renegotiation": False,
                    },
                    "certinfo": {
                        "certificate_matches_hostname": False,
                        "certificate_untrusted": [],
                    },
                    "has_vulnerabilities": True,
                    "flag_for_finding": True,
                    "has_insecure_protocols": True,
                    "has_insecure_ciphers": True,
                    "has_weak_ciphers": True,
                    "has_weak_protocols": True,
                    "has_cert_issues": True,
                    "has_misconfigurations": False,
                },
            ],
        }

        # Patch API
        self.reptor.api.templates.search = Mock(return_value=[])

        self._load_json_data("sslyze_v5")
        self.sslyze.parsed_input = None
        self.sslyze.parse()
        data = self.sslyze.preprocess_for_template()
        assert isinstance(data, dict)
        data.update(context)

        # Patch preprocess_for_template
        self.sslyze.preprocess_for_template = Mock(return_value=data)
        self.sslyze.generate_findings()
        assert len(self.sslyze.findings) == 1

        summary = "We found that example.com:443 and 2 other services had a weak TLS setup. This might impact the confidentiality and integrity of your data in transit."

        assert summary in self.sslyze.findings[0].data.summary.value

        certinfo_data = """The certificates of example.com:443 and 2 other services are untrusted by common browsers:

* example.com:443 (unmatching hostname; untrusted by Android, Apple)
* www.example.com:443 (untrusted by Android)
* ftp.example.com:443 (unmatching hostname)"""
        assert certinfo_data in self.sslyze.findings[0].data.description.value

        misconfigurations_data = """Additionally, we detected the following misconfigurations:

|  | TLS Compression | Downgrade (no SCSV fallback) | No Secure Renegotiation | Client Renegotiation |
| ------- | ------- | ------- | ------- | ------- |
| example.com:443 |  <span style="color: green">No</span> | <span style="color: red">Yes</span> | <span style="color: red">Yes</span> | <span style="color: green">No</span> |
| www.example.com:443 |  <span style="color: red">Yes</span> | <span style="color: red">Yes</span> | <span style="color: red">Yes</span> | <span style="color: red">Yes</span> |
| ftp.example.com:443 |  <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: green">No</span> |"""
        assert misconfigurations_data in self.sslyze.findings[0].data.description.value

        vulnerabilities_data = """example.com:443 and 2 other services used outdated TLS libraries. This results in the following vulnerabilities:


|  | Heartbleed | Robot Attack | OpenSSL CCS |
| ------- | ------- | ------- | ------- |
| example.com:443 |  <span style="color: red">Vulnerable</span> | <span style="color: green">OK</span> | <span style="color: green">OK</span> |
| www.example.com:443 |  <span style="color: green">OK</span> | <span style="color: red">Vulnerable</span> | <span style="color: green">OK</span> |
| ftp.example.com:443 |  <span style="color: green">OK</span> | <span style="color: green">OK</span> | <span style="color: red">Vulnerable</span> |"""
        assert vulnerabilities_data in self.sslyze.findings[0].data.description.value

        protocols_data = """We also found out that example.com:443 and 2 other services had insecure ciphers or protocols enabled:

|  | SSLv2 | SSLv3 | TLS 1.0 | TLS 1.1 | Weak Ciphers | Insecure Ciphers |
| ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| example.com:443 |  <span style="color: red">Yes</span> | <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: orange">Yes</span> | <span style="color: red">Yes</span> |
| www.example.com:443 |  <span style="color: green">No</span> | <span style="color: red">Yes</span> | <span style="color: green">No</span> | <span style="color: orange">Yes</span> | <span style="color: orange">Yes</span> | <span style="color: green">No</span> |
| ftp.example.com:443 |  <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: green">No</span> | <span style="color: orange">Yes</span> | <span style="color: red">Yes</span> |"""
        assert protocols_data in self.sslyze.findings[0].data.description.value

    def test_generate_and_push_findings(self):
        # Patch API
        self.reptor.api.templates.search = Mock(return_value=[])

        self._load_json_data("sslyze_v5")
        # Assert "create_finding" is called if no findings exist
        self.sslyze.reptor.api.projects.get_findings = Mock(return_value=[])
        self.reptor.api.projects.create_finding = MagicMock()

        self.sslyze.generate_and_push_findings()
        assert self.reptor.api.projects.create_finding.called

        # Assert "create_finding" is not called if finding with same title exists
        finding_raw = FindingRaw(
            {"data": {"title": "Weak TLS setup might impact encryption"}}
        )
        self.reptor.api.projects._project_dict = {"project_type": ""}
        self.reptor.api.project_designs.project_design = ProjectDesign()
        self.reptor.api.projects.get_findings = Mock(return_value=[finding_raw])
        self.reptor.api.projects.create_finding = MagicMock()

        self.sslyze.generate_and_push_findings()
        assert not self.sslyze.reptor.api.projects.create_finding.called

    def test_generate_findings(self):
        # Patch API
        self.reptor.api.templates.search = Mock(return_value=[])

        self._load_json_data("sslyze_v5")
        self.sslyze.generate_findings()
        assert len(self.sslyze.findings) == 1
        fndg = self.sslyze.findings[0]
        assert fndg.data.title.value == "Weak TLS setup might impact encryption"
        assert (
            "had insecure ciphers or protocols enabled" in fndg.data.description.value
        )
        assert (
            fndg.data.affected_components.value[0].value
            == "www.example.com:443 (127.0.0.1)"
        )
        assert [r.value for r in fndg.data.references.value] == [
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
                        "sslv2": {"weak_ciphers": [], "insecure_ciphers": []},
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
                            ],
                            "insecure_ciphers": [],
                        },
                    },
                    "has_weak_protocols": False,
                    "has_insecure_protocols": True,
                    "has_weak_ciphers": True,
                    "has_insecure_ciphers": False,
                    "certinfo": {
                        "certificate_matches_hostname": True,
                        "has_sha1_in_certificate_chain": False,
                        "certificate_untrusted": ["Android"],
                    },
                    "has_cert_issues": True,
                    "vulnerabilities": {
                        "heartbleed": True,
                        "openssl_ccs": True,
                        "robot": False,
                    },
                    "has_vulnerabilities": True,
                    "misconfigurations": {
                        "compression": False,
                        "downgrade": True,
                        "client_renegotiation": False,
                        "no_secure_renegotiation": True,
                    },
                    "has_misconfigurations": True,
                    "flag_for_finding": True,
                    "has_insecure_protocols": True,
                    "has_insecure_ciphers": False,
                    "has_cert_issues": True,
                    "has_misconfigurations": True,
                }
            ]
        }
        self._load_json_data("sslyze_v5")
        self.sslyze.parsed_input = None
        self.sslyze.parse()
        data = self.sslyze.preprocess_for_template()
        assert data == result

    def test_format(self):
        # result = """| Host | Port | Service | Version |"""
        self._load_json_data("sslyze_v5")

        # Protocols template
        protocols_result = """# Sslyze

## 🚩 www.example.com:443 (127.0.0.1)


**Protocols**

 * <span style="color: red">SSLv2</span>
 * <span style="color: green">TLS 1.2</span>


**Certificate Information**

 * <span style="color: red">Certificate untrusted by:</span>
    * Android
 * Certificate matches hostname: <span style="color: green">Yes</span>
 * SHA1 in certificate chain: <span style="color: green">No</span>


**Vulnerabilities**

 * Heartbleed: <span style="color: red">Yes</span>
 * Robot Attack: <span style="color: green">No</span>
 * OpenSSL CCS (CVE-2014-0224): <span style="color: red">Yes</span>


**Misconfigurations**

 * Compression: <span style="color: green">No</span>
 * Downgrade Attack (no SCSV fallback): <span style="color: red">Yes</span>
 * No Secure Renegotiation: <span style="color: red">Yes</span>
 * Client Renegotiation: <span style="color: green">No</span>


**Weak Cipher Suites**

 * <span style="color: orange">DHE-RSA-AES256-SHA256</span> (TLS 1.2)
 * <span style="color: orange">AES256-SHA256</span> (TLS 1.2)
 * <span style="color: orange">ECDHE-RSA-AES256-SHA384</span> (TLS 1.2)
 * <span style="color: orange">DHE-RSA-AES256-SHA</span> (TLS 1.2)
 * <span style="color: orange">AES256-SHA</span> (TLS 1.2)
 * <span style="color: orange">AES256-GCM-SHA384</span> (TLS 1.2)
 * <span style="color: orange">DHE-RSA-AES128-SHA256</span> (TLS 1.2)
 * <span style="color: orange">DHE-RSA-AES128-SHA</span> (TLS 1.2)
 * <span style="color: orange">AES128-SHA</span> (TLS 1.2)
 * <span style="color: orange">AES128-SHA256</span> (TLS 1.2)
 * <span style="color: orange">AES128-GCM-SHA256</span> (TLS 1.2)
 * <span style="color: orange">ECDHE-RSA-AES128-SHA256</span> (TLS 1.2)"""
        self.sslyze.format()
        assert self.sslyze.formatted_input.strip() == protocols_result.strip()

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
            "summary",
            "misconfigurations",
            "protocols",
            "vulnerabilities",
            "weak_ciphers",
        ]
        assert all([t in templates for t in template_names])
