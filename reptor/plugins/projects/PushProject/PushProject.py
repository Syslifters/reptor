import argparse
import contextlib
import json
import sys
import typing
from pathlib import Path
from io import FileIO

import tomli

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.Section import Section as SectionModel
from reptor.models.Finding import Finding as FindingModel
from reptor.models.ProjectDesign import ProjectDesign


class PushProject(UploadBase):
    """ """

    meta = {
        "name": "PushProject",
        "summary": "Push data to project from JSON or TOML",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projectdata: typing.Optional[FileIO] = kwargs.get("projectdata")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        parser.add_argument("projectdata", nargs="?", type=argparse.FileType("rb"))

    def run(self):
        content = None
        if self.projectdata:
            content = self.projectdata.read().decode()
        project_data = self._read_input(content=content)

        # Get project data to map report fields to sections
        project = self.reptor.api.projects.project
        project_design = self.reptor.api.project_designs.project_design
        # Map fields to sections
        sections_data = dict()
        for section in project.sections:
            sections_data[section.id] = {"data": {}}
            for report_field_name, report_field_data in project_data.get(
                "report_data", {}
            ).items():
                if report_field_name in section.fields:
                    sections_data[section.id]["data"][
                        report_field_name
                    ] = report_field_data

        # Check for valid report field data format
        error = False
        for section_id, section_data in sections_data.items():
            try:
                SectionModel(
                    section_data,
                    project_design,
                    raise_on_unknown_fields=False,
                )
            except ValueError:
                error = True

        # Check for valid finding field data format
        findings = project_data.get("findings", [])
        for finding in findings:
            try:
                FindingModel(finding, project_design, raise_on_unknown_fields=False)
            except ValueError:
                error = True

        ## Upload
        if not error:
            for section_id, section_data in sections_data.items():
                self.reptor.api.projects.update_section(section_id, section_data)
            for finding in findings:
                self.reptor.api.projects.create_finding(finding)
        else:
            raise ValueError("Invalid data format")

        report_field_count = len(project_data.get("report_data", {}))
        if report_field_count > 0:
            self.log.success(
                f"Successfully updated {report_field_count} report field{'s'[:report_field_count^1]}"
            )

        findings_count = len(findings)
        if findings_count > 0:
            self.log.success(
                f"Successfully uploaded {findings_count} finding{'s'[:findings_count^1]}"
            )

    def _read_input(self, content: typing.Optional[str] = None) -> dict:
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

        # Create model to assure compatibility of predefined fields
        assert isinstance(loaded_content, dict)
        report_data = loaded_content.get("report_data", {})
        assert isinstance(report_data, dict)
        SectionModel(
            {"data": report_data}, ProjectDesign(), raise_on_unknown_fields=False
        )
        findings = loaded_content.get("findings", [])
        assert isinstance(findings, list)
        for finding in findings:
            assert isinstance(finding, dict)
            FindingModel(finding, ProjectDesign(), raise_on_unknown_fields=False)
        return loaded_content


loader = PushProject
