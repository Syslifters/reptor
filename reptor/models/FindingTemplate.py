import typing
from copy import deepcopy

from reptor.models.Base import BaseModel, FindingTemplateSources
from reptor.models.Finding import FindingDataRaw


class FindingTemplateTranslation(BaseModel):
    language: str = "en-US"
    status: str = "in-progress"
    is_main: bool = True
    data: FindingDataRaw

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict:
        result = deepcopy(vars(self))
        result["data"] = self.data.to_dict()
        return result


class FindingTemplate(BaseModel):
    """
    Attributes:
        details:
        images:
        usage_count:
        source:
        tags:
        translations:
    """

    details: str = ""
    images: str = ""
    usage_count: int = 0
    source: FindingTemplateSources = FindingTemplateSources.CREATED
    tags: typing.List[str] = []
    translations: typing.List[FindingTemplateTranslation] = []

    def to_dict(self) -> dict:
        result = deepcopy(vars(self))
        if isinstance(self.source, FindingTemplateSources):
            result["source"] = self.source.value
        result["translations"] = [t.to_dict() for t in self.translations]
        return result
