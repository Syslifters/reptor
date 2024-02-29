from django.utils.html import strip_tags

from reptor.lib.importers.BaseImporter import BaseImporter
from reptor.models.UserConfig import UserConfig

import requests

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

    #TO DO
    mapping = {
        "title": "title",
        "cvssv3_score": "cvss",
        "description": "summary",
        "severity": "impact",
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
            raise ValueError(
                "DefectDojo API Key is required. Add to your user config."
            )
        self.insecure = kwargs.get("insecure", False)

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

    def _get_defectdojo_findings(self):

        # Include the Authorization Token that it may be used
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.apikey}",
        }

        try:
            response = requests.get(f"{self.defectdojo_url}/api/v2/findings/?active=true&false_p=false&is_mitigated=false", headers=headers, timeout=60)
            result = response.json().get("results", [])
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        finally:
            for r in result:
                r["references"] = self.strip_references(r["references"])
        return result

    def next_findings_batch(self):
        self.debug("Running batch findings")

        findings = self._get_defectdojo_findings()
        for finding_data in findings:
            yield {
                "language": "en-US",
                "is_main": True,
                "status": "in-progress",
                "data": finding_data,
            }


loader = DefectDojo
