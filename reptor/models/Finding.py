import typing

from reptor.models.Base import BaseModel
from reptor.models.ProjectDesign import ProjectDesign
from reptor.models.Section import (
    SectionData,
    SectionDataField,
    SectionDataRaw,
)


class FindingDataRaw(SectionDataRaw):
    """
    This data class holds the finding field raw values (usually, strings or lists).  
    The objects of this class may hold other attributes, depending on your SysReptor project design and custom finding fields.

    Attributes:
        title (str): Finding title.
        cvss (str): CVSS score.
        summary (str): Finding summary.
        description (str): Detailed description of the finding.
        precondition (str): Finding precondition.
        impact (str): Finding impact.
        recommendation (str): Finding recommendation.
        short_recommendation (str): Finding short recommendation.
        references (List[str]): List of references (e.g., external URLs) related to the finding.
        affected_components (List[str]): List of affected components.
        owasp_top10_2021 (str): OWASP Top 10 2021 category (e.g., `A01_2021`, `A02_2021`, etc.).
        wstg_category (str): WSTG category (e.g., `INFO`, `CONF`, `IDNT`, `ATHN`, etc.).
        retest_notes (str): Retest notes.
        retest_status (str): Retest status (one of `open`, `resolved`, `partial`, `changed`, `accepted`).
        severity (str): Finding severity (one of `info`, `low`, `medium`, `high`, `critical`).

    Methods:
        to_dict(): Convert to a dictionary representation.
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
    severity: str = ""

    def __str__(self):
        return self.title
    
    def __repr__(self):
        return f'FindingDataRaw(title="{self.title}", id="{self.id}")'


class FindingDataField(SectionDataField):
    """
    `FindingDataField` holds the finding field definition, metadata and its value.

    Attributes:
        id (str): Finding field ID (e.g., `summary`).
        type (ProjectFieldTypes): Finding field type (e.g., `cvss`, `string`, `markdown`, etc.).
        label (str): Human-readable label of the field (displayed in SysReptor UI).
        origin (str): Field origin (one of `core`, `predefined`, `custom`)
        default (str): Default value of the field (if any).
        required (bool): Whether the field is required.
        spellcheck (bool): Whether the field value should be spellchecked.
        properties (List['ProjectDesignField']): Nested fields. Used for object fields.
        choices (List[dict]): List of choices for enum fields.
        items (dict): Items for list fields.
        suggestions (List[str]): Suggestions for combobox fields.
        value (str | List | bool | float | FindingDataField]): The value of the field. Type depends on the field type:

            - `str`: For cvss, string, markdown, enum, user, combobox, date fields
            - `List`: For list fields
            - `bool`: For boolean fields
            - `float`: For number fields
            - `FindingDataField`: For object fields (holds nested `FindingDataField`)

    Methods:
        to_dict(): Convert to a dictionary representation.
    """

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'FindingDataField(name="{self.name}", type="{self.type}", value="{self.value}")'


class FindingData(SectionData):
    """
    Finding data holds finding field values and field metadata.

    Attributes:
        id (str): Finding data ID (uuid).
        created (datetime): Finding creation time.
        updated (datetime): Finding last update time.

        title (FindingDataField): Finding title field.
        cvss (FindingDataField): CVSS score field.
        summary (FindingDataField): Finding summary field.
        description (FindingDataField): Detailed description field.
        precondition (FindingDataField): Finding precondition field.
        impact (FindingDataField): Finding impact field.
        recommendation (FindingDataField): Finding recommendation field.
        short_recommendation (FindingDataField): Finding short recommendation field.
        references (FindingDataField): Finding references field.
        affected_components (FindingDataField): Affected components field.
        owasp_top10_2021 (FindingDataField): OWASP Top 10 2021 category field.
        wstg_category (FindingDataField): WSTG category field.
        retest_notes (FindingDataField): Retest notes field.
        retest_status (FindingDataField): Retest status field.
        severity (FindingDataField): Finding severity field.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
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
    severity: FindingDataField

    field_class = FindingDataField

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        kwargs.setdefault("strict_type_check", True)
        super().__init__(*args, **kwargs)
    
    def __str__(self):
        return str(self.title.value)
    
    def __repr__(self):
        return f'FindingData(title="{self.title.value}")'


class FindingRaw(BaseModel):
    """
    Attributes:
        id (str): Finding ID (uuid).
        created (datetime): Finding creation time.
        updated (datetime): Finding last update time.

        project (str): Project ID (uuid).
        project_type (str): Project design ID.
        language (str): Language code (e.g., "en-US").
        template (str): Finding template ID (if any).
        assignee (str): User ID of the assignee.
        status (str): Status of the finding (e.g., "in-progress", etc.).
        order (int): Order of the finding in the project (if finding order is overridden).
        data (FindingDataRaw): Finding field data.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    project: str = ""
    project_type: str = ""
    language: str = ""
    template: str = ""
    assignee: str = ""
    status: str = "in-progress"
    order: int = 0
    data: FindingDataRaw

    def __init__(self, data, *args, **kwargs):
        if "data" not in data:
            data["data"] = dict()
        super().__init__(data, *args, **kwargs)
    
    def __str__(self):
        return self.data.title
    
    def __repr__(self):
        return f'FindingRaw(title="{self.data.title}", id="{self.id}")'


class Finding(FindingRaw):
    """
    `Finding` has the same attributes as `FindingRaw`, but the `data` attribute is an instance of `FindingData` class, which performs type checks and holds allowed values and other field metadata.

    Attributes:
        data (FindingData): Finding field data with type checks and metadata.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """

    data: FindingData

    def __init__(
        self,
        raw: typing.Union[FindingRaw, typing.Dict],
        project_design: ProjectDesign,
        strict_type_check: bool = False,
    ):
        if isinstance(raw, dict):
            raw = FindingRaw(raw)

        # Set attributes from FindingRaw
        for attr in typing.get_type_hints(FindingRaw).items():
            self.__setattr__(attr[0], raw.__getattribute__(attr[0]))
        self.data = FindingData(
            raw.data,
            project_design.finding_fields,
            strict_type_check=strict_type_check
        )
    
    def __str__(self):
        return self.data.title
    
    def __repr__(self):
        return f'Finding(title="{self.data.title}", id="{self.id}")'

    @classmethod
    def from_translation(
        cls,
        translation: typing.Any,  # translation = FindingTemplateTranslation
        **kwargs,
    ):
        raw = FindingRaw(
            {"language": translation.language, "data": translation.data.to_dict()}
        )
        return cls(raw, **kwargs)
