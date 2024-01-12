import typing

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.models.Note import NoteTemplate


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
        self.notetitle = kwargs.get("notetitle") or "Sslyze"
        self.note_icon = "🔒"
        self.input_format = "json"

    protocol_mapping = {
        "ssl_2_0_cipher_suites": "sslv2",
        "ssl_3_0_cipher_suites": "sslv3",
        "tls_1_0_cipher_suites": "tlsv1",
        "tls_1_1_cipher_suites": "tlsv1_1",
        "tls_1_2_cipher_suites": "tlsv1_2",
        "tls_1_3_cipher_suites": "tlsv1_3",
    }

    # Taken from https://ciphersuite.info/
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
    weak_protocols = ["tlsv1", "tlsv1_1"]
    insecure_protocols = ["sslv2", "sslv3"]

    def get_protocols(self, target):
        result_protocols = dict()
        for protocol, protocol_data in target["scan_result"].items():
            protocol = self.protocol_mapping.get(protocol)
            if (protocol_data.get("result") or {}).get("accepted_cipher_suites"):
                result_protocols[protocol] = {}
        return result_protocols

    def get_weak_ciphers(self, target):
        result_protocols = dict()
        for protocol, protocol_data in target["scan_result"].items():
            protocol = self.protocol_mapping.get(protocol)
            if (protocol_data.get("result") or {}).get("accepted_cipher_suites"):
                result_protocols.setdefault(protocol, dict())
                weak_ciphers = list(
                    filter(
                        None,
                        [
                            c["cipher_suite"]["openssl_name"]
                            if c["cipher_suite"]["openssl_name"] in self.weak_ciphers
                            else None
                            for c in protocol_data["result"]["accepted_cipher_suites"]
                        ],
                    )
                )
                result_protocols[protocol]["weak_ciphers"] = weak_ciphers
                insecure_ciphers = list(
                    filter(
                        None,
                        [
                            c["cipher_suite"]["openssl_name"]
                            if c["cipher_suite"]["openssl_name"]
                            in self.insecure_ciphers
                            else None
                            for c in protocol_data["result"]["accepted_cipher_suites"]
                        ],
                    )
                )
                result_protocols[protocol]["insecure_ciphers"] = insecure_ciphers
        return result_protocols

    def get_certinfo(self, target):
        result_certinfo = dict()
        certinfo = (
            target.get("scan_result", dict()).get("certificate_info", {}).get("result")
        )
        if certinfo is None:
            return result_certinfo
        deployments = certinfo.get("certificate_deployments", list())
        result_certinfo["certificate_matches_hostname"] = all(
            deployment.get("leaf_certificate_subject_matches_hostname", True)
            for deployment in deployments
        )
        result_certinfo["has_sha1_in_certificate_chain"] = all(
            deployment.get("verified_chain_has_sha1_signature", True)
            for deployment in deployments
        )
        path_validation_results = [
            deployment.get("path_validation_results", list())
            for deployment in deployments
        ]
        path_validation_results = [x for l in path_validation_results for x in l]
        result_certinfo["certificate_untrusted"] = list(
            filter(
                None,
                [
                    validation.get("trust_store", {}).get("name")
                    if not validation.get("was_validation_successful", True)
                    else None
                    for validation in path_validation_results
                ],
            )
        )
        return result_certinfo

    def get_vulnerabilities(self, target):
        result_vulnerabilities = dict()
        commands_results = target.get("scan_result")
        if commands_results is None:
            return result_vulnerabilities
        result_vulnerabilities["heartbleed"] = (
            commands_results.get("heartbleed", dict())
            .get("result", dict())
            .get("is_vulnerable_to_heartbleed", False)
        )
        result_vulnerabilities["openssl_ccs"] = (
            commands_results.get("openssl_ccs_injection", dict())
            .get("result", dict())
            .get("is_vulnerable_to_ccs_injection")
        )
        robot = (
            commands_results.get("robot", dict())
            .get("result", dict())
            .get("robot_result")
        )
        result_vulnerabilities["robot"] = (
            robot if "NOT_VULNERABLE" not in robot else False
        )
        return result_vulnerabilities

    def get_misconfigurations(self, target):
        result_misconfigs = dict()
        commands_results = target.get("scan_result")
        if commands_results is None:
            return result_misconfigs
        result_misconfigs["compression"] = (
            commands_results.get("tls_compression", dict())
            .get("result", dict())
            .get("supports_compression")
        )
        result_misconfigs["downgrade"] = (
            commands_results.get("tls_fallback_scsv", dict())
            .get("result", dict())
            .get("supports_fallback_scsv", True)
            is not True
        )
        result_misconfigs["client_renegotiation"] = (
            commands_results.get("session_renegotiation", dict())
            .get("result", dict())
            .get("is_vulnerable_to_client_renegotiation_dos")
        )
        result_misconfigs["no_secure_renegotiation"] = (
            commands_results.get("session_renegotiation", dict())
            .get("result", dict())
            .get("supports_secure_renegotiation", True)
            is not True
        )
        return result_misconfigs

    def get_server_info(self, target):
        result_server_info = dict()
        server_info = target.get("server_location")
        result_server_info["hostname"] = server_info["hostname"]
        result_server_info["port"] = str(server_info["port"])
        result_server_info["ip_address"] = server_info["ip_address"]
        return result_server_info

    def create_notes(self):
        data = self.preprocess_for_template()
        # Create note structure
        ## Main note
        main_note = NoteTemplate()
        main_note.title = self.notetitle
        main_note.icon_emoji = self.note_icon

        ## Subnotes per target
        for target in data.get("data", list()):
            target_note = NoteTemplate()
            target_note.title = (
                f"{target['hostname']}:{target['port']} ({target['ip_address']})"
            )
            if target["flag_for_finding"]:
                target_note.title = f"🚩 {target_note.title}"
            target_note.checked = False
            target_note.template = "summary"
            target_note.template_data = target
            main_note.children.append(target_note)
        return main_note

    def preprocess_for_template(self) -> dict:
        data = list()
        if not isinstance(self.parsed_input, dict):
            return dict()
        for target in self.parsed_input.get("server_scan_results", list()):
            target_data = self.get_server_info(target)

            target_data["protocols"] = self.get_protocols(target)
            target_data["protocols"].update(self.get_weak_ciphers(target))

            target_data["has_weak_protocols"] = False
            if any(p in target_data["protocols"] for p in self.weak_protocols):
                target_data["has_weak_protocols"] = True

            target_data["has_insecure_protocols"] = False
            if any(p in target_data["protocols"] for p in self.insecure_protocols):
                target_data["has_insecure_protocols"] = True

            target_data["has_weak_ciphers"] = False
            if any(
                [
                    v.get("weak_ciphers", list())
                    for _, v in target_data["protocols"].items()
                ]
            ):
                target_data["has_weak_ciphers"] = True
            target_data["has_insecure_ciphers"] = False
            if any(
                [
                    v.get("insecure_ciphers", list())
                    for _, v in target_data["protocols"].items()
                ]
            ):
                target_data["has_insecure_ciphers"] = True

            target_data["certinfo"] = self.get_certinfo(target)

            target_data["has_cert_issues"] = False
            if any(
                [
                    target_data["certinfo"].get("certificate_untrusted"),
                    target_data["certinfo"].get("has_sha1_in_certificate_chain"),
                    not target_data["certinfo"].get("certificate_matches_hostname"),
                ]
            ):
                target_data["has_cert_issues"] = True

            target_data["vulnerabilities"] = self.get_vulnerabilities(target)
            target_data["has_vulnerabilities"] = False
            if any([v for k, v in target_data["vulnerabilities"].items()]):
                target_data["has_vulnerabilities"] = True
            target_data["misconfigurations"] = self.get_misconfigurations(target)

            target_data["has_misconfigurations"] = False
            if any([v for k, v in target_data["misconfigurations"].items()]):
                target_data["has_misconfigurations"] = True

            target_data["flag_for_finding"] = any(
                [
                    target_data["has_insecure_protocols"],
                    target_data["has_insecure_ciphers"],
                    target_data["has_vulnerabilities"],
                    target_data["has_cert_issues"],
                    target_data["has_misconfigurations"],
                ]
            )
            data.append(target_data)
        return {
            "data": data,
        }

    def finding_weak_tls_setup(self):
        finding_context = self.preprocess_for_template()
        if finding_context is None:
            return None

        # Remove targets false "flag_for_finding"
        finding_context["data"] = [
            d for d in finding_context["data"] if d["flag_for_finding"]
        ]

        finding_context["affected_components_short"] = [
            f'{t["hostname"]}:{t["port"]}' for t in finding_context["data"]
        ]
        finding_context["affected_components"] = [
            f'{t["hostname"]}:{t["port"]} ({t["ip_address"]})'
            for t in finding_context["data"]
        ]
        finding_context["has_vulnerabilities"] = any(
            [t["has_vulnerabilities"] for t in finding_context["data"]]
        )
        finding_context["has_insecure_protocols"] = any(
            [t["has_insecure_protocols"] for t in finding_context["data"]]
        )
        finding_context["has_insecure_ciphers"] = any(
            [t["has_insecure_ciphers"] for t in finding_context["data"]]
        )
        finding_context["has_cert_issues"] = any(
            [t["has_cert_issues"] for t in finding_context["data"]]
        )
        finding_context["has_misconfigurations"] = any(
            [t["has_misconfigurations"] for t in finding_context["data"]]
        )
        if any(
            [
                finding_context["has_insecure_protocols"],
                finding_context["has_insecure_ciphers"],
                finding_context["has_vulnerabilities"],
                finding_context["has_cert_issues"],
                finding_context["has_misconfigurations"],
            ]
        ):
            return finding_context
        return None


loader = Sslyze
