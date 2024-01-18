import datetime
import enum
import logging
import typing
from copy import deepcopy
from dataclasses import dataclass


@dataclass
class BaseModel:
    """
    Base Model
    """

    id: str = ""
    created: datetime.datetime = datetime.datetime.now()
    updated: datetime.datetime = datetime.datetime.now()
    _log = logging.getLogger("reptor")

    def __init__(self, data: typing.Optional[typing.Dict] = None):
        if data:
            self._fill_from_api(data)

    def _get_combined_class_type_hints(self) -> dict:
        type_hints = list()
        type_hints_from_class = self.__class__
        while type_hints_from_class.__base__:
            type_hints.append(typing.get_type_hints(type_hints_from_class))
            if type_hints_from_class == BaseModel:
                break
            type_hints_from_class = type_hints_from_class.__base__

        combined_class_type_hints = dict()
        for type_hint in reversed(type_hints):
            combined_class_type_hints.update(type_hint)
        return combined_class_type_hints

    def _fill_from_api(self, data: typing.Dict):
        """Fills Model from reptor.api return JSON data

        Args:
            data (str): API Return Data
        """
        # Import here to prevent circular imports
        from reptor.models.Finding import FindingDataRaw
        from reptor.models.FindingTemplate import (FindingTemplate,
                                                   FindingTemplateTranslation)
        from reptor.models.Note import Note
        from reptor.models.Project import Project
        from reptor.models.ProjectDesign import (ProjectDesign,
                                                 ProjectDesignField)
        from reptor.models.Section import SectionDataRaw
        from reptor.models.User import User

        combined_class_type_hints = self._get_combined_class_type_hints()

        for attr in combined_class_type_hints.items():
            if attr[0] in data:
                # Check if one of our models, then proceed recursively
                try:
                    model_class = attr[1].__args__[0]
                    is_list = True
                except AttributeError:
                    model_class = attr[1]
                    is_list = False

                if model_class in [
                    User,
                    FindingTemplate,
                    FindingDataRaw,
                    SectionDataRaw,
                    Note,
                    Project,
                    ProjectDesign,
                    FindingTemplateTranslation,
                ]:
                    if is_list:
                        item_list = list()
                        for item in data[attr[0]]:
                            item_list.append(model_class(item))
                        self.__setattr__(attr[0], item_list)
                    else:
                        self.__setattr__(attr[0], model_class(data[attr[0]]))
                elif model_class == ProjectDesignField:
                    self.__setattr__(attr[0], list())
                    for k, v in data[attr[0]].items():
                        v["name"] = k
                        self.__getattribute__(attr[0]).append(model_class(v))
                else:
                    # Fill each attribute
                    self.__setattr__(attr[0], data[attr[0]])

    def to_dict(self):
        dict_values = deepcopy(vars(self))
        for k, v in dict_values.items():
            if isinstance(v, datetime.datetime):
                dict_values[k] = v.isoformat()
            elif isinstance(v, list):
                try:
                    dict_values[k] = [i.to_dict() for i in v]
                except AttributeError:
                    dict_values[k] = v
            else:
                try:
                    dict_values[k] = v.to_dict()  # type: ignore
                except AttributeError:
                    pass
        return dict_values


class ProjectFieldTypes(enum.Enum):
    cvss = "cvss"
    string = "string"
    markdown = "markdown"
    list = "list"
    object = "object"
    enum = "enum"
    user = "user"
    combobox = "combobox"
    date = "date"
    number = "number"
    boolean = "boolean"


class FindingTemplateSources(enum.Enum):
    CREATED = "created"
    IMPORTED = "imported"
    IMPORTED_DEPENDENCY = "imported_dependency"
    CUSTOMIZED = "customized"
    SNAPSHOT = "snapshot"
