import typing

from reptor.models.Base import BaseModel
from reptor.models.Finding import Finding
from reptor.models.ProjectDesign import ProjectDesign
from reptor.models.Section import Section
from reptor.models.User import User


class ProjectBase(BaseModel):
    name: str = ""
    project_type: str = ""  # is the project design id
    language: str = ""
    tags: typing.List[str] = []
    readonly: bool = False
    source: str = ""
    copy_of: str = ""
    override_finding_order: bool = False
    members: typing.List[User] = []
    imported_members: typing.List[User] = []
    details: str = ""
    notes: str = ""
    images: str = ""


class Project(ProjectBase):
    findings: typing.List[Finding] = []
    sections: typing.List[Section] = []

    def __init__(self, data: dict, project_design: ProjectDesign):
        if isinstance(data.get("findings"), str):
            raise ValueError("Findings should be list. Use ProjectOverview instead.")
        if isinstance(data.get("sections"), str):
            raise ValueError("Sections should be list. Use ProjectOverview instead.")
        super().__init__(data)
        self.findings = list()
        self.sections = list()
        for finding in data.get("findings", []):
            self.findings.append(Finding(finding, project_design))
        for section in data.get("sections", []):
            self.sections.append(Section(section, project_design))
        # Order findings by their order attribute
        self.findings.sort(key=lambda f: f.order, reverse=True)


class ProjectOverview(ProjectBase):
    findings: str = ""
    sections: str = ""

    def __init__(self, data: dict):
        if isinstance(data.get("findings"), list):
            raise ValueError("Findings should be str. Use Project instead.")
        if isinstance(data.get("sections"), list):
            raise ValueError("Sections should be str. Use Project instead.")
        super().__init__(data)
