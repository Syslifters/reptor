import json
import sys
import contextlib

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
        finding = self._read_finding()
        self.reptor.api.projects.create_finding(finding.to_dict())
        self.log.success("Finding uploaded successfully")

    def _read_finding(self, content=None) -> FindingModel:
        if content is None:
            # Read finding from stdin
            self.info("Reading from stdin...")
            content = sys.stdin.read()

        with contextlib.suppress(json.JSONDecodeError):
            content = json.loads(content, strict=False)
        if not isinstance(content, dict):
            with contextlib.suppress(toml.TomlDecodeError):
                content = toml.loads(content)
        if not isinstance(content, dict):
            raise ValueError("Could not decode stdin (excepted JSON or TOML)")
        return FindingModel(content, force_compatible=False)


loader = Finding
