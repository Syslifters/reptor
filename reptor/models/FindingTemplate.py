import typing

from reptor.models.Base import BaseModel, FindingTemplateSources
from reptor.models.Finding import FindingDataRaw


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
