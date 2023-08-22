import typing

from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignField
from reptor.models.Section import (
    SectionData,
    SectionDataField,
    SectionDataRaw,
    SectionRaw,
)


class FindingDataRaw(SectionDataRaw):
    """
    Custom finding fields will be added as additional attributes.

    Attributes:
        title:
        cvss:
        summary:
        description:
        precondition:
        impact:
        recommendation:
        short_recommendation:
        references:
        affected_components:
        owasp_top10_2021:
        wstg_category:
        retest_notes:
        retest_status:
        evidence:
    """

    title: str = ""
    cvss: str = ""
    summary: str = ""
    description: str = ""
    precondition: str = ""
    impact: str = ""
    recommendation: str = ""
    short_recommendation: str = ""
    references: typing.List[str] = []
    affected_components: typing.List[str] = []
    owasp_top10_2021: str = ""
    wstg_category: str = ""
    retest_notes: str = ""
    retest_status: str = ""
    evidence: str = ""
    severity: str = ""

    def to_json(self) -> dict:
        return vars(self)


class FindingDataField(SectionDataField):
    ...


class FindingData(SectionData):
    title: FindingDataField
    cvss: FindingDataField
    summary: FindingDataField
    description: FindingDataField
    precondition: FindingDataField
    impact: FindingDataField
    recommendation: FindingDataField
    short_recommendation: FindingDataField
    references: FindingDataField
    affected_components: FindingDataField
    owasp_top10_2021: FindingDataField
    wstg_category: FindingDataField
    retest_notes: FindingDataField
    retest_status: FindingDataField
    evidence: FindingDataField

    field_class = FindingDataField

    def __init__(
        self, design_fields: typing.List[ProjectDesignField], data_raw: FindingDataRaw
    ):
        super().__init__(design_fields, data_raw)


class FindingRaw(SectionRaw):
    data: FindingDataRaw


class Finding(FindingRaw):
    data: FindingData

    def __init__(
        self,
        raw: typing.Union[FindingRaw, typing.Dict],
        project_design: typing.Optional[ProjectDesign] = None,
    ):
        if project_design is None:
            project_design = ProjectDesign()
        if isinstance(raw, dict):
            raw = FindingRaw(raw)

        # Set attributes from FindingRaw
        for attr in typing.get_type_hints(FindingRaw).items():
            self.__setattr__(attr[0], raw.__getattribute__(attr[0]))
        self.data = FindingData(project_design.finding_fields, raw.data)
