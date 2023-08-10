from reptor.lib.importers.BaseImporter import BaseImporter

try:
    from gql import Client, gql
    from gql.transport.aiohttp import AIOHTTPTransport
    from gql.transport.exceptions import TransportServerError
except ImportError:
    gql = None

# Todo: This needs a lot of work
# Consider it a WIP Example


class GhostWriter(BaseImporter):
    """
    Imports findings from GhostWriter

    Connects to the API of a GhostWriter instance and imports its
    finding templates.
    """

    meta = {
        "author": "Richard Schwabe",
        "name": "GhostWriter",
        "version": "1.0",
        "license": "MIT",
        "summary": "Imports GhostWriter finding templates",
    }

    mapping = {
        "cvss_vector": "cvss",
        "description": "description",
        "impact": "impact",
        "mitigation": "recommendation",
        "references": "references",
        "title": "title",
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
        super().add_arguments(parser, plugin_filepath)
        action_group = parser.add_argument_group()
        action_group.add_argument(
            "-url",
            "--url",
            metavar="URL",
            action="store",
            const="",
            nargs="?",
            help="API Url",
        )

    def convert_references(self, value):
        return value.splitlines()

    def _get_ghostwriter_findings(self):
        query = gql(
            """
            query MyQuery {
                finding {
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
            yield finding_data


loader = GhostWriter
