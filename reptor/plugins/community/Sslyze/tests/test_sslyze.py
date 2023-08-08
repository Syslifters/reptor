import json
import os
import unittest

import django
from django.conf import settings
from django.utils.functional import empty

from reptor.lib.conf import settings as reptor_settings
from reptor.lib.reptor import Reptor

from ..Sslyze import Sslyze

templates_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../templates'))
reptor_settings.TEMPLATES[0]['DIRS'].append(templates_path)
settings.configure(reptor_settings, DEBUG=True)
django.setup()


class SslyzeTests(unittest.TestCase):
    def setUp(self) -> None:
        reptor = Reptor()
        Sslyze.set_template_vars(os.path.dirname(templates_path))
        self.sslyze = Sslyze(reptor=reptor)

        return super().setUp()

    def _load_json_data(self):
        self.sslyze.input_format = 'json'
        filepath = os.path.join(
            os.path.dirname(__file__), './data/sslyze.json')
        with open(filepath, 'r') as f:
            self.sslyze.raw_input = f.read()

    def test_parse(self):
        result_dict = {"a": "b"}
        self.sslyze.raw_input = json.dumps(result_dict)
        self.sslyze.parse()
        self.assertEqual(self.sslyze.parsed_input, result_dict)

    def test_process_parsed_input_for_template(self):
        result = {"data": [{"hostname": "www.example.com", "port": 443, "ip_address": "127.0.0.1", "protocols": {"tlsv1_2": {"weak_ciphers": ["DHE-RSA-AES256-SHA256", "AES256-SHA256", "ECDHE-RSA-AES256-SHA384", "DHE-RSA-AES256-SHA", "AES256-SHA", "AES256-GCM-SHA384", "DHE-RSA-AES128-SHA256", "DHE-RSA-AES128-SHA", "AES128-SHA", "AES128-SHA256", "AES128-GCM-SHA256", "ECDHE-RSA-AES128-SHA256"]}}, "has_weak_ciphers": True, "certinfo": {"certificate_matches_hostname": True, "has_sha1_in_certificate_chain": False, "certificate_untrusted": []}, "vulnerabilities": {"heartbleed": False, "openssl_ccs": False, "robot": False}, "has_vulnerabilities": False, "misconfigurations": {"compression": False, "downgrade": False, "client_renegotiation": False, "no_secure_renegotiation": False}}]}
        self._load_json_data()
        self.sslyze.parsed_input = None
        self.sslyze.parse()
        data = self.sslyze.process_parsed_input_for_template()
        self.assertEqual(data, result)

    def test_format(self):
        #result = """| Host | Port | Service | Version |"""
        self._load_json_data()

        # Protocols template
        protocols_result = '    * <span style="color: green">TLS 1.2</span>\n'
        self.sslyze.template = 'protocols'
        self.sslyze.format()
        self.assertEqual(self.sslyze.formatted_input, protocols_result)
        
        # certinfo template
        certinfo_result = """ * <span style="color: green">Certificate is trusted</span>
 * Certificate matches hostname: 
<span style="color: green">
    Yes
</span>
 * SHA1 in certificate chain: 
<span style="color: green">
    No
</span>
"""
        self.sslyze.template = 'certinfo'
        self.sslyze.format()
        self.assertEqual(self.sslyze.formatted_input, certinfo_result)

        # vulnerabilities template
        vulnerabilities_result = """ * Heartbleed: 
<span style="color: green">
    No
</span>
 * Robot Attack: 
<span style="color: green">
    No
</span>
 * OpenSSL CCS (CVE-2014-0224): 
<span style="color: green">
    No
</span>
"""
        self.sslyze.template = 'vulnerabilities'
        self.sslyze.format()
        self.assertEqual(self.sslyze.formatted_input, vulnerabilities_result)

        # misconfigurations template
        misconfigurations_result = """ * Compression: 
<span style="color: green">
    No
</span>
 * Downgrade Attack (no SCSV fallback): 
<span style="color: green">
    No
</span>
 * No Secure Renegotiation: 
<span style="color: green">
    No
</span>
 * Client Renegotiation: 
<span style="color: green">
    No
</span>
"""
        self.sslyze.template = 'misconfigurations'
        self.sslyze.format()
        self.assertEqual(self.sslyze.formatted_input, misconfigurations_result)

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
        self.sslyze.template = 'weak_ciphers'
        self.sslyze.format()
        self.assertEqual(self.sslyze.formatted_input, weak_ciphers_result)

        # summary template
        self.sslyze.template = 'default_summary'
        self.sslyze.format()
        for content in [certinfo_result, vulnerabilities_result, misconfigurations_result, weak_ciphers_result, protocols_result]:
            self.assertIn(content, self.sslyze.formatted_input) # type: ignore