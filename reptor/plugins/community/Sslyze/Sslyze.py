import json
from reptor.lib.plugins.ToolBase import ToolBase


class Sslyze(ToolBase):
    """
    target="app1.example.com:443{127.0.0.1} app2.example.com:443{127.0.0.2}"
    sslyze --sslv2 --sslv3 --tlsv1 --tlsv1_1 --tlsv1_2 --tlsv1_3 --certinfo --reneg --http_get --hide_rejected_ciphers --compression --heartbleed --openssl_ccs --fallback --robot "$target" --json_out=- | tee sslyze.txt | reptor sslyze

    # Format and upload
    cat sslyze_result.txt | reptor ssylyze -c upload
    """

    meta = {
        "author": "Syslifters",
        "name": "Sslyze",
        "version": "1.0",
        "license": "MIT",
        "tags": ["web", "ssl"],
        "summary": "format sslyze JSON output",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.note_icon = "🔒"

    weak_ciphers = [
        "DHE-DSS-DES-CBC3-SHA",
        "DHE-DSS-AES128-SHA",
        "DHE-DSS-AES128-SHA256",
        "DHE-DSS-AES256-SHA",
        "DHE-DSS-AES256-SHA256",
        "DHE-DSS-CAMELLIA128-SHA",
        "DHE-DSS-CAMELLIA128-SHA256",
        "DHE-DSS-CAMELLIA256-SHA",
        "DHE-DSS-CAMELLIA256-SHA256",
        "DHE-DSS-SEED-SHA",
        "DHE-PSK-3DES-EDE-CBC-SHA",
        "DHE-PSK-AES128-CBC-SHA",
        "DHE-PSK-AES128-CBC-SHA256",
        "DHE-PSK-AES256-CBC-SHA",
        "DHE-PSK-AES256-CBC-SHA384",
        "DHE-PSK-CAMELLIA128-SHA256",
        "DHE-PSK-CAMELLIA256-SHA384",
        "DHE-RSA-DES-CBC3-SHA",
        "DHE-RSA-AES128-SHA",
        "DHE-RSA-AES128-SHA256",
        "DHE-RSA-AES256-SHA",
        "DHE-RSA-AES256-SHA256",
        "DHE-RSA-CAMELLIA128-SHA",
        "DHE-RSA-CAMELLIA128-SHA256",
        "DHE-RSA-CAMELLIA256-SHA",
        "DHE-RSA-CAMELLIA256-SHA256",
        "DHE-RSA-SEED-SHA",
        "ECDHE-ECDSA-DES-CBC3-SHA",
        "ECDHE-ECDSA-AES128-SHA",
        "ECDHE-ECDSA-AES128-SHA256",
        "ECDHE-ECDSA-AES256-SHA",
        "ECDHE-ECDSA-AES256-SHA384",
        "ECDHE-ECDSA-CAMELLIA128-SHA256",
        "ECDHE-ECDSA-CAMELLIA256-SHA384",
        "ECDHE-PSK-3DES-EDE-CBC-SHA",
        "ECDHE-PSK-AES128-CBC-SHA",
        "ECDHE-PSK-AES128-CBC-SHA256",
        "ECDHE-PSK-AES256-CBC-SHA",
        "ECDHE-PSK-AES256-CBC-SHA384",
        "ECDHE-PSK-CAMELLIA128-SHA256",
        "ECDHE-PSK-CAMELLIA256-SHA384",
        "ECDHE-RSA-DES-CBC3-SHA",
        "ECDHE-RSA-AES128-SHA",
        "ECDHE-RSA-AES128-SHA256",
        "ECDHE-RSA-AES256-SHA",
        "ECDHE-RSA-AES256-SHA384",
        "ECDHE-RSA-CAMELLIA128-SHA256",
        "ECDHE-RSA-CAMELLIA256-SHA384",
        "PSK-3DES-EDE-CBC-SHA",
        "PSK-AES128-CBC-SHA",
        "PSK-AES128-CBC-SHA256",
        "PSK-AES128-CCM",
        "PSK-AES128-CCM8",
        "PSK-AES128-GCM-SHA256",
        "PSK-AES256-CBC-SHA",
        "PSK-AES256-CBC-SHA384",
        "PSK-AES256-CCM",
        "PSK-AES256-CCM8",
        "PSK-AES256-GCM-SHA384",
        "PSK-CAMELLIA128-SHA256",
        "PSK-CAMELLIA256-SHA384",
        "PSK-CHACHA20-POLY1305",
        "RSA-PSK-3DES-EDE-CBC-SHA",
        "RSA-PSK-AES128-CBC-SHA",
        "RSA-PSK-AES128-CBC-SHA256",
        "RSA-PSK-AES128-GCM-SHA256",
        "RSA-PSK-AES256-CBC-SHA",
        "RSA-PSK-AES256-CBC-SHA384",
        "RSA-PSK-AES256-GCM-SHA384",
        "RSA-PSK-CAMELLIA128-SHA256",
        "RSA-PSK-CAMELLIA256-SHA384",
        "RSA-PSK-CHACHA20-POLY1305",
        "DES-CBC3-SHA",
        "AES128-SHA",
        "AES128-SHA256",
        "AES128-CCM",
        "AES128-CCM8",
        "AES128-GCM-SHA256",
        "AES256-SHA",
        "AES256-SHA256",
        "AES256-CCM",
        "AES256-CCM8",
        "AES256-GCM-SHA384",
        "CAMELLIA128-SHA",
        "CAMELLIA128-SHA256",
        "CAMELLIA256-SHA",
        "CAMELLIA256-SHA256",
        "IDEA-CBC-SHA",
        "SEED-SHA",
        "SRP-DSS-3DES-EDE-CBC-SHA",
        "SRP-DSS-AES-128-CBC-SHA",
        "SRP-DSS-AES-256-CBC-SHA",
        "SRP-RSA-3DES-EDE-CBC-SHA",
        "SRP-RSA-AES-128-CBC-SHA",
        "SRP-RSA-AES-256-CBC-SHA",
        "SRP-3DES-EDE-CBC-SHA",
        "SRP-AES-128-CBC-SHA",
        "SRP-AES-256-CBC-SHA",
    ]
    insecure_ciphers = [
        "ADH-DES-CBC3-SHA",
        "ADH-AES128-SHA",
        "ADH-AES128-SHA256",
        "ADH-AES128-GCM-SHA256",
        "ADH-AES256-SHA",
        "ADH-AES256-SHA256",
        "ADH-AES256-GCM-SHA384",
        "ADH-CAMELLIA128-SHA",
        "ADH-CAMELLIA128-SHA256",
        "ADH-CAMELLIA256-SHA",
        "ADH-CAMELLIA256-SHA256",
        "ADH-SEED-SHA",
        "DHE-PSK-NULL-SHA",
        "DHE-PSK-NULL-SHA256",
        "DHE-PSK-NULL-SHA384",
        "AECDH-DES-CBC3-SHA",
        "AECDH-AES128-SHA",
        "AECDH-AES256-SHA",
        "AECDH-NULL-SHA",
        "ECDHE-ECDSA-NULL-SHA",
        "ECDHE-PSK-NULL-SHA",
        "ECDHE-PSK-NULL-SHA256",
        "ECDHE-PSK-NULL-SHA384",
        "ECDHE-RSA-NULL-SHA",
        "PSK-NULL-SHA",
        "PSK-NULL-SHA256",
        "PSK-NULL-SHA384",
        "RSA-PSK-NULL-SHA",
        "RSA-PSK-NULL-SHA256",
        "RSA-PSK-NULL-SHA384",
        "NULL-MD5",
        "NULL-SHA",
        "NULL-SHA256",
    ]

    def get_weak_ciphers(self, target):
        result_protocols = dict()
        for protocol, protocol_data in target["commands_results"].items():
            if len(protocol_data.get("accepted_cipher_list", list())) > 0:
                result_protocols[protocol] = dict()
                weak_ciphers = list(
                    filter(
                        None,
                        [
                            c["openssl_name"]
                            if c["openssl_name"] in self.weak_ciphers
                            else None
                            for c in protocol_data["accepted_cipher_list"]
                        ],
                    )
                )
                if weak_ciphers:
                    result_protocols[protocol]["weak_ciphers"] = weak_ciphers
                insecure_ciphers = list(
                    filter(
                        None,
                        [
                            c["openssl_name"]
                            if c["openssl_name"] in self.insecure_ciphers
                            else None
                            for c in protocol_data["accepted_cipher_list"]
                        ],
                    )
                )
                if insecure_ciphers:
                    result_protocols[protocol]["insecure_ciphers"] = insecure_ciphers
        return result_protocols

    def get_certinfo(self, target):
        result_certinfo = dict()
        certinfo = target.get("commands_results", dict()).get("certinfo")
        if certinfo is None:
            return result_certinfo
        result_certinfo["certificate_matches_hostname"] = certinfo.get(
            "certificate_matches_hostname"
        )
        result_certinfo["has_sha1_in_certificate_chain"] = certinfo.get(
            "has_sha1_in_certificate_chain"
        )
        result_certinfo["certificate_untrusted"] = list(
            filter(
                None,
                [
                    store["trust_store"]["name"]
                    if not store["is_certificate_trusted"]
                    else None
                    for store in certinfo.get("path_validation_result_list") or list()
                ],
            )
        )
        return result_certinfo

    def get_vulnerabilities(self, target):
        result_vulnerabilities = dict()
        commands_results = target.get("commands_results")
        if commands_results is None:
            return result_vulnerabilities
        result_vulnerabilities["heartbleed"] = commands_results.get(
            "heartbleed", dict()
        ).get("is_vulnerable_to_heartbleed")
        result_vulnerabilities["openssl_ccs"] = commands_results.get(
            "openssl_ccs", dict()
        ).get("is_vulnerable_to_ccs_injection")
        result_vulnerabilities["robot"] = commands_results.get("robot", dict()).get(
            "robot_result_enum"
        ) in ["VULNERABLE_STRONG_ORACLE", "VULNERABLE_WEAK_ORACLE"]
        return result_vulnerabilities

    def get_misconfigurations(self, target):
        result_misconfigs = dict()
        commands_results = target.get("commands_results")
        if commands_results is None:
            return result_misconfigs
        result_misconfigs["compression"] = (
            commands_results.get("compression", dict()).get("compression_name")
            is not None
        )
        result_misconfigs["downgrade"] = (
            commands_results.get("fallback", dict()).get("supports_fallback_scsv", True)
            is not True
        )
        result_misconfigs["client_renegotiation"] = commands_results.get(
            "reneg", dict()
        ).get("accepts_client_renegotiation")
        result_misconfigs["no_secure_renegotiation"] = (
            commands_results.get("reneg", dict()).get(
                "supports_secure_renegotiation", True
            )
            is not True
        )

        return result_misconfigs

    def get_server_info(self, target):
        result_server_info = dict()
        server_info = target.get("server_info")
        result_server_info["hostname"] = server_info["hostname"]
        result_server_info["port"] = server_info["port"]
        result_server_info["ip_address"] = server_info["ip_address"]
        return result_server_info

    def parse(self):
        super().parse()
        parsed = list()
        if self.raw_input:
            ssylze_json = json.loads(self.raw_input)
            for target in ssylze_json.get("accepted_targets", list()):
                target_data = self.get_server_info(target)
                target_data["protocols"] = self.get_weak_ciphers(target)
                target_data["certinfo"] = self.get_certinfo(target)
                target_data["vulnerabilities"] = self.get_vulnerabilities(target)
                target_data["misconfigurations"] = self.get_misconfigurations(target)

                parsed.append(target_data)
        self.parsed_input = parsed

    def format(self):
        super().format()
        formatted = ""
        for target in self.parsed_input:
            # Heading
            formatted += (
                f"# {target['hostname']}:{target['port']} ({target['ip_address']})\n\n"
            )
            # Protocols
            formatted += "**Protocols**\n\n"
            if "sslv2" in target["protocols"]:
                formatted += ' * <span style="color: red">SSLv2</span>\n'
            if "sslv3" in target["protocols"]:
                formatted += ' * <span style="color: red">SSLv3</span>\n'
            if "tlsv1" in target["protocols"]:
                formatted += ' * <span style="color: red">TLS 1.0</span>\n'
            if "tlsv1_1" in target["protocols"]:
                formatted += ' * <span style="color: red">TLS 1.1</span>\n'
            if "tlsv1_2" in target["protocols"]:
                formatted += ' * <span style="color: green">TLS 1.2</span>\n'
            if "tlsv1_3" in target["protocols"]:
                formatted += ' * <span style="color: green">TLS 1.3</span>\n'
            formatted += "\n\n"

            # Certificate Info
            formatted += "**Certificate Information**: \n\n"
            if not target["certinfo"]["certificate_untrusted"]:
                formatted += (
                    ' * <span style="color: green">Certificate is trusted</span>\n'
                )
            else:
                formatted += (
                    ' * <span style="color: red">Certificate untrusted by:</span>\n'
                )
                for store in target["certinfo"]["certificate_untrusted"]:
                    formatted += f"    * {store}\n"

            formatted += (
                f" * Certificate matches hostname: "
                f'<span style="color: '
                f"{'green' if target['certinfo']['certificate_matches_hostname'] else 'red'}\">"
                f"{'Yes' if target['certinfo']['certificate_matches_hostname'] else 'No'}</span>\n"
            )

            formatted += (
                f" * SHA1 in certificate chain: "
                f'<span style="color: '
                f"{'red' if target['certinfo']['has_sha1_in_certificate_chain'] else 'green'}\">"
                f"{'Yes' if target['certinfo']['has_sha1_in_certificate_chain'] else 'No'}</span>\n"
            )

            formatted += "\n\n"

            # Vulnerabilities
            if any([v for k, v in target["vulnerabilities"].items()]):
                formatted += "**Vulnerabilities**: "
                vulns = list()
                vulns.append("Heartbleed") if target["vulnerabilities"].get(
                    "heartbleed"
                ) else True
                vulns.append("Robot Attack") if target["vulnerabilities"].get(
                    "robot"
                ) else True
                vulns.append("OpenSSL CCS (CVE-2014-0224)") if target[
                    "vulnerabilities"
                ].get("openssl_ccs") else True
                formatted += ", ".join(vulns) + "\n\n"
            # Misconfigurations
            if any([v for k, v in target["misconfigurations"].items()]):
                formatted += "**Misconfigurations**: "
                misconfigs = list()
                misconfigs.append("Compression") if target["misconfigurations"].get(
                    "compression"
                ) else True
                misconfigs.append("Downgrade Attack (no SCSV fallback)") if target[
                    "misconfigurations"
                ].get("downgrade") else True
                misconfigs.append("No Secure Renegotiation") if target[
                    "misconfigurations"
                ].get("no_secure_renegotiation") else True
                misconfigs.append("Client Renegotiation") if target[
                    "misconfigurations"
                ].get("accepts_client_renegotiation") else True
                formatted += ", ".join(misconfigs) + "\n\n"

            # Weak ciphers
            if any(
                [
                    v.get("weak_ciphers", list()) + v.get("insecure_ciphers", list())
                    for k, v in target["protocols"].items()
                ]
            ):
                formatted += "**Weak Cipher Suites**\n\n"
                if target["protocols"].get("sslv2"):
                    formatted += " * **SSLv2**\n"
                    for c in target["protocols"]["sslv2"].get(
                        "insecure_ciphers", list()
                    ):
                        formatted += (
                            f'    * {c} (<span style="color: red">insecure</span>)\n'
                        )
                    for c in target["protocols"]["sslv2"].get("weak_ciphers", list()):
                        formatted += f"    * {c}\n"
                if target["protocols"].get("sslv3"):
                    formatted += " * **SSLv3**\n"
                    for c in target["protocols"]["sslv3"].get(
                        "insecure_ciphers", list()
                    ):
                        formatted += (
                            f'    * {c} (<span style="color: red">insecure</span>)\n'
                        )
                    for c in target["protocols"]["sslv3"].get("weak_ciphers", list()):
                        formatted += f"    * {c}\n"
                if target["protocols"].get("tlsv1"):
                    formatted += " * **TLS 1.0**\n"
                    for c in target["protocols"]["tlsv1"].get(
                        "insecure_ciphers", list()
                    ):
                        formatted += (
                            f'    * {c} (<span style="color: red">insecure</span>)\n'
                        )
                    for c in target["protocols"]["tlsv1"].get("weak_ciphers", list()):
                        formatted += f"    * {c}\n"
                if target["protocols"].get("tlsv1_1"):
                    formatted += " * **TLS 1.1**\n"
                    for c in target["protocols"]["tlsv1_1"].get(
                        "insecure_ciphers", list()
                    ):
                        formatted += (
                            f'    * {c} (<span style="color: red">insecure</span>)\n'
                        )
                    for c in target["protocols"]["tlsv1_1"].get("weak_ciphers", list()):
                        formatted += f"    * {c}\n"
                if target["protocols"].get("tlsv1_2"):
                    formatted += " * **TLS 1.2**\n"
                    for c in target["protocols"]["tlsv1_2"].get(
                        "insecure_ciphers", list()
                    ):
                        formatted += (
                            f'    * {c} (<span style="color: red">insecure</span>)\n'
                        )
                    for c in target["protocols"]["tlsv1_2"].get("weak_ciphers", list()):
                        formatted += f"    * {c}\n"
                if target["protocols"].get("tlsv1_3"):
                    formatted += " * **TLS 1.3**\n"
                    for c in target["protocols"]["tlsv1_3"].get(
                        "insecure_ciphers", list()
                    ):
                        formatted += (
                            f'    * {c} (<span style="color: red">insecure</span>)\n'
                        )
                    for c in target["protocols"]["tlsv1_3"].get("weak_ciphers", list()):
                        formatted += f"    * {c}\n"
            formatted += "\n\n"

        self.formatted_input = formatted


loader = Sslyze
