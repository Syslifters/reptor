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
    
    def __str__(self):
        return self.language
    
    def __repr__(self):
        return f'FindingTemplateTranslation(language="{self.language}", is_main={self.is_main})'


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

    def get_main_title(self) -> str:
        return self.get_main_translation().data.title
    
    def get_main_translation(self) -> FindingTemplateTranslation:
        for translation in self.translations:
            if translation.is_main:
                return translation
    
    def __str__(self):
        return self.get_main_title()
    
    def __repr__(self):
        return f'FindingTemplate(title="{self.get_main_title()}", id="{self.id}")'
