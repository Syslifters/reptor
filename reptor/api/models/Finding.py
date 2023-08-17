from reptor.api.models.Base import BaseModel
from reptor.api.models.Project import ProjectDesign, ProjectDesignField
from reptor.api.models.Section import SectionData, SectionDataField, SectionDataRaw, SectionRaw


import typing

from reptor.api.models.Base import FindingTemplateSources
from reptor.lib.interfaces.api.models import FindingProtocol


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


class FindingTemplateTranslation(BaseModel):
    language: str = "en-US"
    status: str = "in-progress"
    is_main: bool = True
    data: FindingDataRaw

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Init mandatory fields
        self.is_main = True

    def to_json(self) -> dict:
        result = vars(self)
        result["data"] = self.data.to_json()
        return result


class FindingTemplate(BaseModel):
    """
    Attributes:
        details:
        images:
        lock_info:
        usage_count:
        source:
        tags:
        translations:
    """

    details: str = ""
    images: str = ""
    lock_info: bool = False
    usage_count: int = 0
    source: FindingTemplateSources = FindingTemplateSources.CREATED
    tags: typing.List[str] = []
    translations: typing.List[FindingTemplateTranslation] = []

    def to_json(self) -> dict:
        result = vars(self)
        if isinstance(self.source, FindingTemplateSources):
            result["source"] = self.source.value
        result["translations"] = [t.to_json() for t in self.translations]
        return result


class Finding(FindingRaw, FindingProtocol):
    data: FindingData

    def __init__(self, project_design: ProjectDesign, raw: FindingRaw):
        # Set attributes from FindingRaw
        for attr in typing.get_type_hints(FindingRaw).items():
            self.__setattr__(attr[0], raw.__getattribute__(attr[0]))

        self.data = FindingData(project_design.finding_fields, raw.data)