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

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'{self.__class__.__name__}(name="{self.name}", id="{self.id}")'


class Project(ProjectBase):
    """
    Attributes:
        id (str): Project ID (uuid).
        created (datetime): Date when the project was created.
        updated (datetime): Date when the project metadata was last updated.
                
        name (str): Project name.
        project_type (str): Project design ID.
        language (str): Project language code (e.g., "en-US").
        tags (List[str]): List of tags associated with the project.
        readonly (bool): Whether the project is read-only (finished).
        source (str): Source of the project design. Possible values: `created`, `imported`, `imported_dependecy`, `customized`, `snapshot`.
        copy_of (str): ID of the project this is a copy of.
        override_finding_order (bool): Whether to override the default finding order.
        members (List[User]): List of project members.
        imported_members (List[User]): List of imported project members (members that are part of an imported project, but do not exist in the SysReptor installation).
        details (str): Project API endpoint (URL).
        notes (str): Project notes API endpoint (URL).
        images (str): Project images API endpoint (URL).

        findings (List[Finding]): List of findings associated with the project.
        sections (List[Section]): List of sections that make up the project.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """


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
        if self.override_finding_order:
            self.findings.sort(key=lambda f: f.order)


class ProjectOverview(ProjectBase):
    """
    `ProjectOverview` has the same attributes as `Project`.  
    The only difference is that it does not contain the `findings` and `sections` attributes, but rather the API endpoints for these resources.

    Attributes:
        findings (str): Findings API endpoint (URL).
        sections (str): Sections API endpoint (URL).

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    findings: str = ""
    sections: str = ""

    def __init__(self, data: dict):
        if isinstance(data.get("findings"), list):
            raise ValueError("Findings should be str. Use Project instead.")
        if isinstance(data.get("sections"), list):
            raise ValueError("Sections should be str. Use Project instead.")
        super().__init__(data)
