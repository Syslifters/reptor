import typing

from reptor.lib.plugins.ToolBase import ToolBase


class Sslyze(ToolBase):
    """
    target="app1.example.com:443{127.0.0.1} app2.example.com:443{127.0.0.2}"
    sslyze --sslv2 --sslv3 --tlsv1 --tlsv1_1 --tlsv1_2 --tlsv1_3 --certinfo --reneg --http_get --hide_rejected_ciphers --compression --heartbleed --openssl_ccs --fallback --robot "$target" --json_out=- | tee sslyze.json | reptor sslyze

    # Format and upload
    cat sslyze.json | reptor sslyze --upload
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
        self.input_format = "json"

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
        robot = commands_results.get("robot", dict()).get("robot_result_enum")
        result_vulnerabilities["robot"] = (
            robot if "NOT_VULNERABLE" not in robot else False
        )
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
        result_server_info["port"] = str(server_info["port"])
        result_server_info["ip_address"] = server_info["ip_address"]
        return result_server_info

    def preprocess_for_template(self):
        data = list()
        if not isinstance(self.parsed_input, dict):
            return None
        for target in self.parsed_input.get("accepted_targets", list()):
            target_data = self.get_server_info(target)
            target_data["protocols"] = self.get_weak_ciphers(target)
            target_data["has_weak_ciphers"] = False
            if any(
                [
                    v.get("weak_ciphers", list()) + v.get("insecure_ciphers", list())
                    for k, v in target_data["protocols"].items()
                ]
            ):
                target_data["has_weak_ciphers"] = True
            target_data["certinfo"] = self.get_certinfo(target)
            target_data["vulnerabilities"] = self.get_vulnerabilities(target)
            target_data["has_vulnerabilities"] = False
            if any([v for k, v in target_data["vulnerabilities"].items()]):
                target_data["has_vulnerabilities"] = True
            target_data["misconfigurations"] = self.get_misconfigurations(target)

            data.append(target_data)
        if self.template in [
            "protocols",
            "certinfo",
            "vulnerabilities",
            "misconfigurations",
            "weak_ciphers",
        ]:
            if len(data) > 1:
                self.log.warning(
                    "sslyze output contains more than one target. Taking the first one."
                )
            return {"target": data[0]}
        return {"data": data}

    def finding_weak_ciphers(self):
        finding_context = self.preprocess_for_template()
        if finding_context is None:
            return None
        if any(
            [
                target.get("has_weak_ciphers")
                for target in finding_context.get("data", [])
            ]
        ):
            # Add affected components
            finding_context["affected_components"] = [
                f'{t["hostname"]}:{t["port"]} ({t["ip_address"]})'
                for t in finding_context["data"]
            ]
            return finding_context
        return None


loader = Sslyze
