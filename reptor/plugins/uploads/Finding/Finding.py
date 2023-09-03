import contextlib
import json
import sys
import typing

import toml

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.Finding import Finding as FindingModel


class Finding(UploadBase):
    """ """

    meta = {
        "name": "Finding",
        "summary": "Uploads findings from JSON or TOML",
    }

    def run(self):
        findings = list(self._read_findings())
        for finding in findings:
            self.reptor.api.projects.create_finding(finding.to_dict())
        findings_count = len(findings)
        self.log.success(
            f"Successfully uploaded {findings_count} finding{'s'[:findings_count^1]}"
        )

    def _read_findings(
        self, content: typing.Optional[str] = None
    ) -> typing.Iterator[FindingModel]:
        if content is None:
            # Read finding from stdin
            self.info("Reading from stdin...")
            content = sys.stdin.read()

        with contextlib.suppress(json.JSONDecodeError):
            content = json.loads(content, strict=False)
        if isinstance(content, str):
            with contextlib.suppress(toml.TomlDecodeError):
                content = toml.loads(content)
        if isinstance(content, str):
            raise ValueError("Could not decode stdin (excepted JSON or TOML)")

        if isinstance(content, dict):
            content = [content]

        for finding in content:
            yield FindingModel(finding, force_compatible=False)


loader = Finding
