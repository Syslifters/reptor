from reptor.lib.importers.BaseImporter import BaseImporter
from reptor.lib.interfaces.reptor import ReptorProtocol

try:
    from gql import gql, Client
    from gql.transport.aiohttp import AIOHTTPTransport
except ImportError:
    from reptor.lib.console import reptor_console

    reptor_console.print("[red]To run this importer you need to install gql[/red]")
    exit(1)

# Todo: This needs a lot of work
# Consider it a WIP Example


class GhostWriter(BaseImporter):
    """
    Author: Richard Schwabe
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: core, import, ghostwriter

    Short Help:
    Imports findings from GhostWriter

    Description:
    Connects to the API of a GhostWriter instance and imports its
    finding templates.

    """

    mapping = {
        "cvss_vector": "cvss",
        "description": "description",
        "impact": "impact",
        "mitigation": "recommendation",
        "references": "references",
        "title": "title",
    }
    ghostwriter_url: str
    ghostwriter_apikey: str

    def __init__(self, reptor: ReptorProtocol, **kwargs) -> None:
        super().__init__(reptor, **kwargs)

        self.ghostwriter_url = kwargs.get("url", "")
        self.ghostwriter_apikey = kwargs.get("apikey", "")
        self.insecure = kwargs.get("insecure", False)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        action_group = parser.add_argument_group()
        action_group.title = "action_group"
        action_group.add_argument(
            "-url",
            "--url",
            metavar="URL",
            action="store",
            const="",
            nargs="?",
            help="API Url",
        )
        action_group.add_argument(
            "-apikey",
            "--apikey",
            metavar="API_KEY",
            action="store",
            const="",
            nargs="?",
            help="API Auth Token from GhostWriter",
        )

    def convert_references(self, value):
        return value.splitlines()

    def _send_graphql_query(self):
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
            "Authorization": f"Bearer {self.ghostwriter_apikey}",
            "x-hasura-admin-secret": f"{self.ghostwriter_apikey}",
            "Content-Type": "application/json",
        }

        transport = AIOHTTPTransport(
            url=f"{self.ghostwriter_url}/v1/graphql", headers=headers
        )

        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(query)
        return result["finding"]

    def next_findings_batch(self):
        self.reptor.logger.debug("Running batch findings")

        findings = self._send_graphql_query()
        for finding_data in findings:
            yield finding_data


loader = GhostWriter
