import contextlib
import json
import sys
import typing

import tomli

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.Finding import Finding as FindingModel
from reptor.models.ProjectDesign import ProjectDesign


class DeleteFindings(UploadBase):
    meta = {
        "name": "DeleteFindings",
        "summary": "Deletes findings by title",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title_contains = kwargs.get("title_contains") or ""
        self.exclude_title_contains = kwargs.get("exclude_title_contains") or ""
        self.no_dry_run = kwargs.get("no_dry_run")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--title-contains",
            metavar="SEARCHTERM",
            action="store",
            dest="title_contains",
            help="Match string in title",
        )
        parser.add_argument(
            "--exclude-title-contains",
            metavar="SEARCHTERM",
            action="store",
            dest="exclude_title_contains",
            help="Matched strings in title are not deleted",
        )
        parser.add_argument(
            "--no-dry-run",
            help="Do delete findings, default is dry-run",
            action="store_true",
        )

    def run(self):
        findings = self.reptor.api.projects.get_findings()
        matched = False
        for finding in findings:
            if self.title_contains.lower() in finding.data.title.lower():
                if (
                    self.exclude_title_contains
                    and self.exclude_title_contains.lower()
                    in finding.data.title.lower()
                ):
                    continue
                matched = True
                if not self.no_dry_run:
                    self.display(f'Would delete finding "{finding.data.title}"')
                else:
                    self.reptor.api.projects.delete_finding(finding.id)
                    self.display(f"Deleted finding {finding.data.title}")

        if not matched:
            self.display("No findings matched.")
        elif not self.no_dry_run:
            self.display('\nDry-run, delete with "--no-dry-run".')


loader = DeleteFindings
