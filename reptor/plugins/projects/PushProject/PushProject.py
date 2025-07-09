import argparse
import contextlib
import json
import sys
import typing

import requests
import tomli

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.Finding import Finding as FindingModel
from reptor.models.ProjectDesign import ProjectDesign
from reptor.models.Section import Section as SectionModel


class PushProject(UploadBase):
    meta = {
        "name": "PushProject",
        "summary": "Push data to project from JSON or TOML",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        projectdata = kwargs.get("projectdata")
        if not isinstance(projectdata, dict):
            content = None
            if projectdata:
                content = projectdata.read().decode()
            content = self._read_input(content=content)
        else:
            content = projectdata

        self.projectdata: dict = content

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        parser.add_argument("projectdata", nargs="?", type=argparse.FileType("rb"))

    def run(self):
        ##### DEPRECATED
        len_sections = len(
            self.reptor.api.projects.update_report_fields(
                self.projectdata.get("report_data", {})
            )
        )
        if len_sections:
            self.log.success(
                f"Updated {len_sections} report section{'s'[:len_sections^1]} using DEPRECATED \"report_data\"."
            )
        ##### END DEPRECATED

        len_sections = len(
            self.reptor.api.projects.update_sections(
                sections=self.projectdata.get("sections", [])
            )
        )
        if len_sections:
            self.log.success(
                f"Updated {len_sections} section{'s'[:len_sections^1]}."
            )
        else:
            self.log.display("No sections updated.")

        # Check for valid finding field data format
        project_design = self.reptor.api.project_designs.project_design
        findings = list()
        for finding in self.projectdata.get("findings", []):
            findings.append(
                (
                    finding,
                    FindingModel(
                        finding, project_design, strict_type_check=False
                    ),  # Checks data format
                )
            )
        # Upload
        for finding, model in findings:
            if model.id:
                # Update existing finding
                try:
                    self.reptor.api.projects.update_finding(model.id, finding)
                    self.log.success(f'Updated finding "{model.data.title.value}".')
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        # Finding with finding id not found
                        # We'll try to create the finding
                        pass
                    else:
                        raise e
                else:
                    continue
            self.reptor.api.projects.create_finding(finding)
            self.log.success(f'Created finding "{model.data.title.value}".')
        if not findings:
            self.log.display("No findings created.")

    def _read_input(self, content: typing.Optional[str] = None) -> dict:
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

        # Create model to assure compatibility of predefined fields
        assert isinstance(loaded_content, dict)

        ##### DEPRECATED
        if "report_data" in loaded_content:
            self.log.warning("The 'report_data' field is deprecated and will be removed in a future version. Use 'sections' instead.")
        report_data = loaded_content.get("report_data", {})
        assert isinstance(report_data, dict)
        SectionModel(
            {"data": report_data}, ProjectDesign(), strict_type_check=False
        )
        ##### END DEPRECATED

        sections = loaded_content.get("sections", [])
        assert isinstance(sections, list)
        for section in sections:
            assert isinstance(section, dict)
            SectionModel(section, ProjectDesign(), strict_type_check=False)

        findings = loaded_content.get("findings", [])
        assert isinstance(findings, list)
        for finding in findings:
            assert isinstance(finding, dict)
            FindingModel(finding, ProjectDesign(), strict_type_check=False)
        return loaded_content


loader = PushProject
