import datetime
import typing
from copy import deepcopy
from typing import Any
from uuid import UUID

from reptor.models.Base import BaseModel, ProjectFieldTypes
from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignField


class SectionDataRaw(BaseModel):
    def _fill_from_api(self, data: typing.Dict):
        """Fills Model from reptor.api return JSON data
        For FindingDataRaw, undefined keys should also be set.

        Args:
            data (str): API Return Data
        """
        for key, value in data.items():
            # We don't care about recursion here
            self.__setattr__(key, value)


class SectionDataField(ProjectDesignField):
    """
    Section data holds values only and does not contain type definitions.
    Most data types cannot be differentiated (like strings and enums).

    This model joins finding data values from an acutal report with project
    design field definitions.
    """

    value: typing.Union[
        str,  # cvss, string, markdown, enum, user, combobox, date
        typing.List,  # list
        bool,  # boolean
        float,  # number
        Any,  # "SectionDataField" for object
    ]

    def __init__(
        self,
        design_field: ProjectDesignField,
        value: typing.Union[
            str,
            typing.List,
            bool,
            float,
            Any,
        ],
        raise_on_unknown_fields: bool = True,
    ):
        # Set attributes from ProjectDesignField
        project_design_type_hints = typing.get_type_hints(ProjectDesignField)
        for attr in project_design_type_hints.items():
            self.__setattr__(attr[0], design_field.__getattribute__(attr[0]))

        if self.type == ProjectFieldTypes.object.value:
            property_value = dict()
            for property in self.properties:
                # property is of type ProjectDesignField
                try:
                    property_value[property.name] = self.__class__(
                        property, value[property.name]
                    )

                except KeyError:
                    if raise_on_unknown_fields:
                        raise KeyError(
                            f"Object name '{property.name}' not found. Did you use "
                            f"wrong project design for your data?"
                        )
            self.value = property_value
        elif self.type == ProjectFieldTypes.list.value:
            self.value = list()
            if not isinstance(value, list):
                raise ValueError(f"Value of '{self.name}' must be list.")
            for v in value:  # type: ignore
                self.value.append(self.__class__(self.items, v))  # type: ignore
        else:
            self.value = value

    def __iter__(self):
        """Recursive iteration through potentially nested SectionDataFields
        returns iterator of SectionDataField"""
        if self.type == ProjectFieldTypes.list.value:
            yield self  # First yield self, then nested fields
            # Iterate through list
            for field in self.value:  # type: ignore
                # Iterate through field for recursion
                for f in field:
                    yield f
        elif self.type == ProjectFieldTypes.object.value:
            yield self  # First yield self, then nested fields
            for _, field in self.value.items():  # type: ignore
                for f in field:
                    yield f
        else:
            yield self

    def __len__(self) -> int:
        return len([e for e in self])

    def to_dict(self) -> typing.Union[dict, list, str]:
        if self.type == ProjectFieldTypes.list.value:
            result = list()
            for subfield in self.value:
                if subfield.type == ProjectFieldTypes.enum.value:
                    valid_enums = [choice["value"] for choice in subfield.choices]
                    if subfield.value in valid_enums:
                        result.append({subfield.name: subfield.value})
                else:
                    result.append(subfield.to_dict())
        elif self.type == ProjectFieldTypes.object.value:
            result = dict()
            for name, subfield in self.value.items():
                if subfield.type == ProjectFieldTypes.enum.value:
                    result[name] = {subfield.name: subfield.value}
                result[name] = subfield.to_dict()
        else:
            return self.value
        return result

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "value" and __value is not None:
            if self.type in [
                ProjectFieldTypes.combobox.value,
                ProjectFieldTypes.cvss.value,
                ProjectFieldTypes.string.value,
                ProjectFieldTypes.markdown.value,
            ]:
                if not isinstance(__value, str):
                    raise ValueError(
                        f"'{self.name}' expects a string value (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.date.value:
                try:
                    datetime.datetime.strptime(__value, "%Y-%m-%d")
                except (ValueError, TypeError):
                    raise ValueError(
                        f"'{self.name}' expects date in format 2000-01-01 (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.enum.value:
                valid_enums = [choice["value"] for choice in self.choices] + [""]
                if __value not in valid_enums:
                    raise ValueError(
                        f"'{__value}' is not an valid enum choice for '{self.name}'."
                    )
            elif self.type == ProjectFieldTypes.list.value:
                if not isinstance(__value, list):
                    raise ValueError(
                        f"Value of '{self.name}' must be list (got '{type(__value)}')."
                    )
                if not all([isinstance(v, self.__class__) for v in __value]):
                    try:
                        # Iterate through list and create objects of self's class
                        if self.items.type in [
                            ProjectFieldTypes.list.value,
                            ProjectFieldTypes.object.value,
                        ]:
                            raise ValueError()

                        new_value = list()
                        for v in __value:
                            if isinstance(v, self.__class__):
                                new_value.append(v)
                            else:
                                new_value.append(self.__class__(self.items, v))
                        __value = new_value
                    except ValueError:
                        raise ValueError(
                            f"Value of '{self.name}' must contain list of {self.__class__.__name__}."
                        )
                types = set([v.type for v in __value])
                if len(types) > 1:
                    raise ValueError(
                        f"Values of '{self.name}' must not contain {self.__class__.__name__}s"
                        f"of multiple types (got {','.join(types)})."
                    )

            elif self.type == ProjectFieldTypes.object.value:
                if not isinstance(__value, dict):
                    raise ValueError(
                        f"Value of '{self.name}' must be dict (got '{type(__value)}')."
                    )
                for k, v in __value.items():
                    if not isinstance(v, self.__class__):
                        raise ValueError(
                            f"Value of '{self.name}' dict values must contain {self.__class__.__name__} "
                            f"(got '{type(v)}' for key '{k}')."
                        )
            elif self.type == ProjectFieldTypes.boolean.value:
                if not isinstance(__value, bool):
                    raise ValueError(
                        f"'{self.name}' expects a boolean value (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.number.value:
                if not isinstance(__value, int) and not isinstance(__value, float):
                    raise ValueError(
                        f"'{self.name}' expects int or float (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.user.value:
                try:
                    UUID(__value, version=4)
                except (ValueError, AttributeError):
                    raise ValueError(
                        f"'{self.name}' expects v4 uuid (got '{__value}')."
                    )

        return super().__setattr__(__name, __value)


class SectionData(BaseModel):
    field_class = SectionDataField

    def __init__(
        self,
        data_raw: SectionDataRaw,
        design_fields: typing.List[ProjectDesignField],
        raise_on_unknown_fields: bool = False,
    ):
        error = False
        for design_field in design_fields:
            try:
                value = data_raw.__getattribute__(design_field.name)
            except AttributeError:
                continue
            try:
                self.__setattr__(
                    design_field.name,
                    self.field_class(
                        design_field,
                        value,
                        raise_on_unknown_fields=raise_on_unknown_fields,
                    ),
                )
            except ValueError as e:
                self._log.error(e)
                error = True
            except KeyError:
                pass

        if raise_on_unknown_fields:
            unknown_fields = [f for f in data_raw.__dict__ if not hasattr(self, f)]
            if len(unknown_fields) > 0:
                if raise_on_unknown_fields:
                    error = True
                self._log.error(
                    f"Incompatible data and designs: Fields in data but not in design: {','.join(unknown_fields)}"
                )
        if error:
            raise ValueError("Invalid data format")

    def __iter__(self):
        """Recursive iteration through cls attributes
        returns FindingDataField"""
        for _, finding_field in vars(self).items():
            for nested_field in finding_field:
                yield nested_field

    def __len__(self) -> int:
        return len([e for e in self])

    def to_dict(self) -> dict:
        result = dict()
        for k, v in deepcopy(vars(self)).items():
            if v.type == ProjectFieldTypes.enum.value:
                valid_enums = [choice["value"] for choice in v.choices]
                if not v.value in valid_enums:
                    # Prevent adding empty enums because server will complain
                    continue
            result[k] = v.to_dict()
        return result


class SectionRaw(BaseModel):
    """
    Attributes:
        project:
        project_type:
        language:
        lock_info:
        template:
        assignee:
        status:
        data:
    """

    project: str = ""
    project_type: str = ""
    language: str = ""
    lock_info: bool = False
    fields: typing.List[str] = []
    template: str = ""
    assignee: str = ""
    status: str = "in-progress"
    data: SectionDataRaw

    def __init__(self, data, *args, **kwargs):
        if "data" not in data:
            data["data"] = dict()
        super().__init__(data, *args, **kwargs)


class Section(SectionRaw):
    data: SectionData

    def __init__(
        self,
        raw: typing.Union[SectionRaw, typing.Dict],
        project_design: typing.Optional[ProjectDesign] = None,
        raise_on_unknown_fields: bool = False,
    ):
        if project_design is None:
            project_design = ProjectDesign()
        if isinstance(raw, dict):
            raw = SectionRaw(raw)

        # Set attributes from SectionRaw
        for attr in typing.get_type_hints(SectionRaw).items():
            self.__setattr__(attr[0], raw.__getattribute__(attr[0]))

        self.data = SectionData(
            raw.data,
            project_design.report_fields,
            raise_on_unknown_fields=raise_on_unknown_fields,
        )
