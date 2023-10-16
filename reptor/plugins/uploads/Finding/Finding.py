import contextlib
import json
import sys
import typing

import tomli

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.Finding import Finding as FindingModel
from reptor.models.ProjectDesign import ProjectDesign


class Finding(UploadBase):
    """ """

    meta = {
        "name": "Finding",
        "summary": "Uploads findings from JSON or TOML",
    }

    def run(self):
        findings = list(self._read_findings())
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
            self.info("Reading from stdin...")
            content = sys.stdin.read()

        loaded_content: typing.Union[None, dict, list] = None
        with contextlib.suppress(json.JSONDecodeError):
            loaded_content = json.loads(content, strict=False)
        if not loaded_content:
            with contextlib.suppress(tomli.TOMLDecodeError):
                loaded_content = tomli.loads(content)
        if not loaded_content:
            raise ValueError("Could not decode stdin (excepted JSON or TOML)")

        if isinstance(loaded_content, dict):
            loaded_content = [loaded_content]

        for finding in loaded_content:
            # Create model to assure compatibility of predefined fields
            assert isinstance(finding, dict)
            FindingModel(finding, ProjectDesign(), raise_on_unknown_fields=False)
            yield finding


loader = Finding
