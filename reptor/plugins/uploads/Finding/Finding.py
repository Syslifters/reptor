import contextlib
import json
import sys
import typing

import tomli

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
            yield FindingModel(finding, force_compatible=False)


loader = Finding
