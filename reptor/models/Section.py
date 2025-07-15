import datetime
import typing
from copy import deepcopy
from typing import Any
from uuid import UUID

from reptor.models.Base import BaseModel, ProjectFieldTypes
from reptor.models.ProjectDesign import ProjectDesign, ProjectDesignField


class SectionDataRaw(BaseModel):
    """
    This data class holds the section field raw values (usually, strings or lists).  
    The objects of this class may hold custom attributes, depending on your SysReptor project design and report fields.

    E.g, if your project design defines a field `executive_summary` of type `string`, then this class will have an attribute `executive_summary` of type `str`.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    def _fill_from_api(self, data: typing.Dict):
        """
        Fills Model from reptor.api return JSON data
        For FindingDataRaw, undefined keys should also be set.

        Args:
            data (str): API Return Data
        """
        for key, value in data.items():
            # We don't care about recursion here
            self.__setattr__(key, value)


class SectionDataField(ProjectDesignField):
    """
    `SectionDataField` holds the section field definition, metadata and its value.

    Attributes:
        id (str): Section field ID (e.g., `executive_summary`).
        type (ProjectFieldTypes): Report field type (e.g., `cvss`, `string`, `markdown`, etc.).
        label (str): Human-readable label of the field (displayed in SysReptor UI).
        origin (str): Field origin (one of `core`, `predefined`, `custom`)
        default (str): Default value of the field (if any).
        required (bool): Whether the field is required.
        spellcheck (bool): Whether the field value should be spellchecked.
        properties (List['ProjectDesignField']): Nested fields. Used for object fields.
        choices (List[dict]): List of choices for enum fields.
        items (dict): Items for list fields.
        suggestions (List[str]): Suggestions for combobox fields.
        value (str | List | bool | float | SectionDataField]): The value of the field. Type depends on the field type:

            - `str`: For cvss, string, markdown, enum, user, combobox, date fields
            - `List`: For list fields
            - `bool`: For boolean fields
            - `float`: For number fields
            - `SectionDataField`: For object fields (holds nested `SectionDataField`)

    Methods:
        to_dict(): Convert to a dictionary representation.
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
        strict_type_check: bool = True,
    ):
        self.strict_type_check = strict_type_check

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
                        property,
                        value[property.name],
                        strict_type_check=strict_type_check,
                    )
                except KeyError:
                    if property.required:
                        raise ValueError(
                            f'"{property.name}" is a required field for "{self.name}".'
                        )
                if strict_type_check and (
                    unknown_fields := [
                        v
                        for v in value.keys()
                        if v not in [p.name for p in self.properties]
                    ]
                ):
                    raise ValueError(
                        f"Unknown fields in {self.name}: {','.join(unknown_fields)}"
                    )
            self.value = property_value
        elif self.type == ProjectFieldTypes.list.value:
            self.value = list()
            if not isinstance(value, list):
                raise ValueError(f"Value of '{self.name}' must be list.")
            for v in value:  # type: ignore
                self.value.append(self.__class__(self.items, v, strict_type_check=strict_type_check))  # type: ignore
        else:
            self.value = value

    def __iter__(self):
        # Recursive iteration through potentially nested SectionDataFields
        # returns iterator of SectionDataField
        if self.type == ProjectFieldTypes.list.value:
            yield self  # First yield self, then nested fields
            # Iterate through list
            for field in self.value:  # type: ignore
                # Iterate through field for recursion
                if isinstance(field, self.__class__):
                    for f in field:
                        yield f
        elif self.type == ProjectFieldTypes.object.value:
            yield self  # First yield self, then nested fields
            for _, field in self.value.items():  # type: ignore
                if isinstance(field, self.__class__):
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
            elif self.type == ProjectFieldTypes.date.value and self.strict_type_check:
                try:
                    datetime.datetime.strptime(__value, "%Y-%m-%d")
                except (ValueError, TypeError):
                    raise ValueError(
                        f"'{self.name}' expects date in format 2000-01-01 (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.enum.value and self.strict_type_check:
                valid_enums = [choice["value"] for choice in self.choices] + [""]
                if __value not in valid_enums:
                    raise ValueError(
                        f"'{__value}' is not an valid enum choice for '{self.name}'."
                    )
            elif self.type == ProjectFieldTypes.list.value:
                if not isinstance(__value, list):
                    if self.strict_type_check:
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

            elif self.type == ProjectFieldTypes.object.value and self.strict_type_check:
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
            elif self.type == ProjectFieldTypes.boolean.value and self.strict_type_check:
                if not isinstance(__value, bool):
                    raise ValueError(
                        f"'{self.name}' expects a boolean value (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.number.value and self.strict_type_check:
                if not isinstance(__value, int) and not isinstance(__value, float):
                    raise ValueError(
                        f"'{self.name}' expects int or float (got '{__value}')."
                    )
            elif self.type == ProjectFieldTypes.user.value and self.strict_type_check:
                try:
                    UUID(__value, version=4)
                except (ValueError, AttributeError):
                    raise ValueError(
                        f"'{self.name}' expects v4 uuid (got '{__value}')."
                    )

        return super().__setattr__(__name, __value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'SectionDataField(name="{self.name}", type="{self.type}", value="{self.value}")'


class SectionData(BaseModel):
    """
    This data class holds the section fields as `SectionDataField` objects.  
    The objects of this class may hold custom attributes, depending on your SysReptor project design and report fields.

    E.g, if your project design defines a field `executive_summary` of type `string`, then this class will have an attribute `executive_summary` of type `SectionDataField` (which in turn specifies allowed values, etc.).

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    field_class = SectionDataField

    def __init__(
        self,
        data_raw: SectionDataRaw,
        design_fields: typing.List[ProjectDesignField],
        strict_type_check: bool = False,
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
                        strict_type_check=strict_type_check,
                    ),
                )
            except ValueError as e:
                self._log.error(e)
                error = True
            except KeyError:
                pass

        if strict_type_check:
            unknown_fields = [f for f in data_raw.__dict__ if not hasattr(self, f)]
            if len(unknown_fields) > 0:
                if strict_type_check:
                    error = True
                self._log.error(
                    f"Incompatible data and designs: Fields in data but not in design: {','.join(unknown_fields)}"
                )
        if error:
            raise ValueError("Invalid data format")

    def __iter__(self):
        # Recursive iteration through cls attributes
        # returns FindingDataField
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
                if v.value not in valid_enums:
                    # Prevent adding empty enums because server will complain
                    continue
            result[k] = v.to_dict()
        return result

    def __str__(self):
        keys = [f'"{k}"' for k in self.to_dict().keys()]
        if len(keys) <= 3:
            return ', '.join(keys)
        else:
            return ', '.join(keys[:3]) + '...'

    def __repr__(self):
        return f'SectionData({self.__str__()})' 


class SectionRaw(BaseModel):
    """
    Attributes:
        id (str): Section ID (e.g., `scope`).
        created (datetime): Section creation time (equals project creation time).
        updated (datetime): Section last update time.

        project (str): Project ID (uuid).
        project_type (str): Project design ID.
        language (str): Language code (e.g., "en-US").
        label (str): Section label (displayed in SysReptor UI).
        fields (List[str]): List of field IDs that are used in this section (e.g., [`executive_summary`]).
        assignee (str): User ID of the assignee.
        status (str): Status of the section (e.g., "in-progress", etc.).
        data (SectionDataRaw): Section field data.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    project: str = ""
    project_type: str = ""
    language: str = ""
    label: str = ""
    fields: typing.List[str] = []
    assignee: str = ""
    status: str = "in-progress"
    data: SectionDataRaw

    def __init__(self, data, *args, **kwargs):
        if "data" not in data:
            data["data"] = dict()
        super().__init__(data, *args, **kwargs)
    
    def __str__(self):
        return self.id
    
    def __repr__(self):
        return f'SectionRaw(id="{self.id}")'


class Section(SectionRaw):
    """
    `Section` has the same attributes as `SectionRaw`, but the `data` attribute is an instance of `SectionData` class, which performs type checks and holds allowed values and other field metadata.

    Attributes:
        data (SectionData): Section field data with type checks and metadata.

    Methods:
        to_dict(): Convert to a dictionary representation.
    """
    data: SectionData

    def __init__(
        self,
        raw: typing.Union[SectionRaw, typing.Dict],
        project_design: typing.Optional[ProjectDesign] = None,
        strict_type_check: bool = False,
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
            strict_type_check=strict_type_check,
        )

    def __str__(self):
        return str(self.id)
    
    def __repr__(self):
        return f'Section(id="{self.id}")'
