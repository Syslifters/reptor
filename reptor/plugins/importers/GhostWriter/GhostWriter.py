from django.utils.html import strip_tags

from reptor.lib.importers.BaseImporter import BaseImporter

try:
    from gql import Client, gql
    from gql.transport.aiohttp import AIOHTTPTransport
    from gql.transport.exceptions import TransportServerError
except ImportError:
    gql = None


class GhostWriter(BaseImporter):
    """
    Imports findings from GhostWriter

    Connects to the GraqhQL API of a GhostWriter instance and imports its
    finding templates to SysReptor via API.
    """

    meta = {
        "author": "Richard Schwabe",
        "name": "GhostWriter",
        "version": "1.0",
        "license": "MIT",
        "summary": "Imports GhostWriter finding templates",
    }

    mapping = {
        "title": "title",
        "cvss_vector": "cvss",
        "description": "summary",
        "findingGuidance": "description",
        "replication_steps": "description",
        "hostDetectionTechniques": "description",
        "networkDetectionTechniques": "description",
        "impact": "impact",
        "mitigation": "recommendation",
        "references": "references",
    }
    ghostwriter_url: str
    apikey: str

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if gql is None:
            raise ImportError(
                "Error importing gql. Install with 'pip install reptor{self.log.escape('[ghostwriter]')}'."
            )

        self.ghostwriter_url = kwargs.get("url", "")
        if not self.ghostwriter_url:
            try:
                self.ghostwriter_url = self.url
            except AttributeError:
                raise ValueError("Ghostwriter URL is required.")
        if not hasattr(self, "apikey"):
            raise ValueError(
                "Ghostwriter API Key is required. Add to your user config."
            )
        self.insecure = kwargs.get("insecure", False)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        action_group = parser.add_argument_group()
        action_group.add_argument(
            "--url",
            metavar="URL",
            action="store",
            const="",
            nargs="?",
            help="Ghostwriter API",
        )

    def convert_references(self, value):
        value = strip_tags(value)
        return [l for l in value.splitlines() if l.strip()]

    def convert_hostDetectionTechniques(self, value):
        if strip_tags(value):
            return f"\n\n**Host Detection Techniques**\n\n{value}"
        return value

    def convert_networkDetectionTechniques(self, value):
        if strip_tags(value):
            return f"\n\n**Network Detection Techniques**\n\n{value}"
        return value

    def convert_findingGuidance(self, value):
        if strip_tags(value):
            return f"TODO: {value}\n\n"
        return value

    def _get_ghostwriter_findings(self):
        query = gql(
            """
            query MyQuery {
                finding {
                        findingGuidance
                        networkDetectionTechniques
                        hostDetectionTechniques
                        replication_steps
                        cvss_vector
                        description
                        impact
                        mitigation
                        references
                        title
                    }
            }
            """
        )

        # Either x-hasura-admin-secret or Authorization Bearer can be used
        headers = {
            "Content-Type": "application/json",
        }
        if (
            self.apikey.startswith("ey")
            and "." in self.apikey
            and len(self.apikey) > 40
        ):
            # Probably a JWT token
            headers["Authorization"] = f"Bearer {self.apikey}"
        else:
            # Probably hasura admin secret
            headers["x-hasura-admin-secret"] = self.apikey

        transport = AIOHTTPTransport(
            url=f"{self.ghostwriter_url}/v1/graphql", headers=headers
        )

        client = Client(transport=transport, fetch_schema_from_transport=False)
        try:
            result = client.execute(query)
        except TransportServerError as e:
            if e.code == 404:
                raise TransportServerError(
                    "404, Not found. Wrong URL? Make sure to specify the graqhql port (default: 8080)."
                ) from e
            raise e
        return result["finding"]

    def next_findings_batch(self):
        self.debug("Running batch findings")

        findings = self._get_ghostwriter_findings()
        for finding_data in findings:
            yield {
                "language": "en-US",
                "status": "in-progress",
                "data": finding_data,
            }


loader = GhostWriter
