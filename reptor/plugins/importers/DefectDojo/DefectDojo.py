import requests

from reptor.lib.importers.BaseImporter import BaseImporter
from reptor.models.UserConfig import UserConfig


class DefectDojo(BaseImporter):
    """
    Imports findings from DefectDojo

    Connects to the GraqhQL API of a DefectDojo instance and imports its
    finding templates to SysReptor via API.
    """

    meta = {
        "author": "Julian Fonticoba",
        "name": "DefectDojo",
        "version": "1.0",
        "license": "MIT",
        "summary": "Imports DefectDojo finding templates",
    }

    # TODO
    mapping = {
        "title": "title",
        "cvssv3_score": "cvss",
        "description": "summary",
        "severity": "severity",
        "mitigation": "recommendation",
        "references": "references",
    }
    defectdojo_url: str
    apikey: str

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.conf:
            return

        self.defectdojo_url = kwargs.get("url", "")
        if not self.defectdojo_url:
            try:
                self.defectdojo_url = self.url
            except AttributeError:
                raise ValueError("DefectDojo URL is required.")
        if not hasattr(self, "apikey"):
            raise ValueError("DefectDojo API Key is required. Add to your user config.")

    @property
    def user_config(self):
        return [
            UserConfig(
                name="url",
                friendly_name="DefectDojo URL",
            ),
            UserConfig(
                name="apikey",
                friendly_name="DefectDojo API key v2",
                redact_current_value=True,
            ),
        ]

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
            help="DefectDojo API",
        )

    def strip_references(self, text):
        if not text:
            return []
        return text.splitlines()

    def _get_defectdojo_findings(self, url=None):
        # Include the Authorization Token that it may be used
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.apikey}",
        }
        return requests.get(
            url
            or f"{self.defectdojo_url}/api/v2/findings/?active=true&false_p=false&is_mitigated=false",
            headers=headers,
            timeout=60,
            verify=not self.reptor.get_config().get("insecure", False),
        ).json()

    def next_findings_batch(self):
        self.debug("Running batch findings")

        next = None
        while True:
            response = self._get_defectdojo_findings(next)
            findings = response.get("results", [])
            for finding_data in findings:
                finding_data["references"] = self.strip_references(
                    finding_data.get("references")
                )
                finding_data["severity"] = (finding_data.get("severity") or "").lower()
                yield {
                    "language": "en-US",
                    "is_main": True,
                    "status": "in-progress",
                    "data": finding_data,
                }
            if not (next := response.get("next")):
                break


loader = DefectDojo
