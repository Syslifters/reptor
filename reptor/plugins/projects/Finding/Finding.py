import contextlib
import json
import sys
import typing

import tomli

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.Finding import Finding as FindingModel
from reptor.models.ProjectDesign import ProjectDesign


class Finding(UploadBase):
    meta = {
        "name": "Finding",
        "summary": "Uploads findings from JSON or TOML",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_finding_id = kwargs.get("update_finding_id", None)

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--update",
            metavar="FINDING ID",
            help="Update finding with the given ID",
            action="store",
            dest="update_finding_id",
            default=None,
        )

    def run(self):
        findings = list(self._read_findings())
        if self.update_finding_id:
            if len(findings) != 1:
                raise ValueError(
                    "When using --update, exactly one finding must be provided"
                )
            self.reptor.api.projects.update_finding(self.update_finding_id, findings[0])
            self.log.success("Successfully updated finding.")
        else:
            for finding in findings:
                self.reptor.api.projects.create_finding(finding)
            findings_count = len(findings)
            self.log.success(
                f"Successfully uploaded {findings_count} finding{'s'[:findings_count^1]}"
            )

    def _read_findings(
        self, content: typing.Optional[str] = None
    ) -> typing.Iterator[dict]:
        if content is None:
            # Read finding from stdin
            self.display("Reading from stdin...")
            content = sys.stdin.read()

        loaded_content: typing.Union[None, dict, list] = None
        with contextlib.suppress(json.JSONDecodeError):
            loaded_content = json.loads(content, strict=False)
        if not loaded_content:
            with contextlib.suppress(tomli.TOMLDecodeError):
                loaded_content = tomli.loads(content)
        if not loaded_content:
            raise ValueError("Could not decode stdin (expected JSON or TOML)")

        if isinstance(loaded_content, dict):
            loaded_content = [loaded_content]

        for finding in loaded_content:
            # Create model to assure compatibility of predefined fields
            assert isinstance(finding, dict)
            FindingModel(finding, ProjectDesign(), strict_type_check=False)
            yield finding


loader = Finding
