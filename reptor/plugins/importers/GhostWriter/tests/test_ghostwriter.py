import json

import pytest

from reptor.lib.conf import Config
from reptor.lib.reptor import Reptor

from .. import GhostWriter


class TestGhostwriter:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config = Config()
        self.reptor._config._raw_config = {}

    def test_init(self):
        self.reptor.get_config()
        with pytest.raises(ValueError):
            # Should raise because of missing URL
            GhostWriter.GhostWriter(reptor=self.reptor)

        with pytest.raises(ValueError):
            # Should raise because of missing API key
            GhostWriter.GhostWriter(reptor=self.reptor, url="test")

        GhostWriter.GhostWriter.apikey = "test"
        GhostWriter.GhostWriter(reptor=self.reptor, url="test")

    def test_get_findings(self):
        finding_data = json.loads(
            '{"finding": [{"cvss_vector": "CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:H", "description": "<p>This finding was part of the Ghostwriter installation.</p>", "impact": "<p>There is a significant risk of ghostwriter being used.</p>", "mitigation": "<p>We recommend to migrate to SysReptor.</p>", "references": "<ul>\\r\\n<li>Ghostwriter docs: https://www.ghostwriter.wiki/</li>\\r\\n<li>SysReptor docs: https://docs.sysreptor.com/</li>\\r\\n</ul>\\r\\n<p>\\u00a0</p>", "title": "High risk of using Ghostwriter"}]}'
        )

        class Client:
            def __init__(*args, **kwargs):
                pass

            def execute(self, *args, **kwargs):
                return finding_data

        # Test x-hasura-admin-secret
        def AIOHTTPTransport(url, headers):  # type: ignore
            assert url == "http://localhost:8080/v1/graphql"
            assert headers == {
                "Content-Type": "application/json",
                "x-hasura-admin-secret": "123456789",
            }

        GhostWriter.AIOHTTPTransport = AIOHTTPTransport
        GhostWriter.Client = Client
        GhostWriter.GhostWriter.apikey = "123456789"
        ghostwriter = GhostWriter.GhostWriter(
            reptor=self.reptor, url="http://localhost:8080"
        )
        assert finding_data["finding"] == ghostwriter._get_ghostwriter_findings()

        # Test Authorization Bearer
        jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE2OTE2NTkzNjUsImV4cCI6MTY5MTY1OTM3NiwiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoianJvY2tldEBleGFtcGxlLmNvbSIsIkdpdmVuTmFtZSI6IkpvaG5ueSIsIlN1cm5hbWUiOiJSb2NrZXQiLCJFbWFpbCI6Impyb2NrZXRAZXhhbXBsZS5jb20iLCJSb2xlIjpbIk1hbmFnZXIiLCJQcm9qZWN0IEFkbWluaXN0cmF0b3IiXX0.xqxBhewa86-Hy2ZiiS_obrjyXZ8vRmqdnDFaFGvXjgU"

        def AIOHTTPTransport(url, headers):
            assert url == "http://localhost:8080/v1/graphql"
            assert headers == {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {jwt_token}",
            }

        GhostWriter.AIOHTTPTransport = AIOHTTPTransport
        GhostWriter.Client = Client
        GhostWriter.GhostWriter.apikey = jwt_token
        ghostwriter = GhostWriter.GhostWriter(
            reptor=self.reptor, url="http://localhost:8080"
        )
        assert finding_data["finding"] == ghostwriter._get_ghostwriter_findings()

    @pytest.mark.parametrize(
        "text,converted",
        [
            ("123\n456", ["123", "456"]),
            ("<ul>\n<li>abc</li>\n<li>cde</li>\n</ul>", ["abc", "cde"]),
        ],
    )
    def test_convert_references(self, text, converted):
        GhostWriter.GhostWriter.apikey = "123456789"
        g = GhostWriter.GhostWriter(reptor=self.reptor, url="http://localhost:8080")
        assert g.convert_references(text) == converted

    @pytest.mark.parametrize(
        "text,converted",
        [
            ("", ""),
            ("ABC", "\n\n**Host Detection Techniques**\n\nABC"),
        ],
    )
    def test_convert_hostDetectionTechniques(self, text, converted):
        GhostWriter.GhostWriter.apikey = "123456789"
        g = GhostWriter.GhostWriter(reptor=self.reptor, url="http://localhost:8080")
        assert g.convert_hostDetectionTechniques(text) == converted

    @pytest.mark.parametrize(
        "text,converted",
        [
            ("", ""),
            ("ABC", "\n\n**Network Detection Techniques**\n\nABC"),
        ],
    )
    def test_convert_networkDetectionTechniques(self, text, converted):
        GhostWriter.GhostWriter.apikey = "123456789"
        g = GhostWriter.GhostWriter(reptor=self.reptor, url="http://localhost:8080")
        assert g.convert_networkDetectionTechniques(text) == converted

    @pytest.mark.parametrize(
        "text,converted",
        [
            ("", ""),
            ("ABC", "TODO: ABC\n\n"),
        ],
    )
    def test_convert_findingGuidance(self, text, converted):
        GhostWriter.GhostWriter.apikey = "123456789"
        g = GhostWriter.GhostWriter(reptor=self.reptor, url="http://localhost:8080")
        assert g.convert_findingGuidance(text) == converted
