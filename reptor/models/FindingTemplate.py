import typing
from copy import deepcopy

from reptor.models.Base import BaseModel, FindingTemplateSources
from reptor.models.Finding import FindingDataRaw


class FindingTemplateTranslation(BaseModel):
    """
    Attributes:
        id (str): Translation ID (uuid).
        created (datetime): Translation creation time.
        updated (datetime): Translation last update time.

        language (str): Language code (e.g., "en-US").
        status (str): Status of the translation (e.g., "in-progress", etc.).
        is_main (bool): Whether this translation is the main one for the finding template.
        data (FindingDataRaw): Finding template data for this translation.
    """
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
        id (str): Finding template ID (uuid).
        created (datetime): Finding template creation time.
        updated (datetime): Finding template last update time.

        translations (List[FindingTemplateTranslation]): List of translations for the finding template. This holds the action finding template data.
        tags (List[str]): List of finding template tags.
        usage_count (int): Number of times the template has been used for creating a finding.
        source (FindingTemplateSources): Source of the finding template (one of `created`, `imported`, `customized`, `imported_dependency`, `snapshot`).
        images (str): Finding template images API endpoint (URL).
        details (str): Finding template details API endpoint (URL).

    Methods:
        get_main_title(): Get the main title of the finding template.
        get_main_translation(): Get the main translation of the finding template.
        to_dict(): Convert to a dictionary representation.
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
