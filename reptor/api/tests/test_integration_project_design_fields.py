import os
from typing import Optional

import pytest

from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.lib.reptor import Reptor
from reptor.models.ProjectDesign import ProjectDesignField


def get_raw_design(api: ProjectDesignsAPI, design_id: str) -> dict:
    response = api.get(f"{api.base_endpoint}{design_id}")
    return response.json()


def field_by_id(fields: list[dict], field_id: str) -> Optional[dict]:
    for field in fields:
        if field.get("id") == field_id:
            return field
    return None


_NOISE_KEYS = {"origin"}
_OMIT_IF_NONE = {"help_text", "cvss_version", "minimum", "maximum", "schema", "pattern"}
_OMIT_IF_EMPTY_STRING = {"id"}


def normalize_field(field: dict, *, ignore_origin: bool = False) -> dict:
    """Normalize a field dict for comparison.

    - Drops ``origin`` when ``ignore_origin`` is True.
    - Strips keys whose value is ``None`` for attrs the server adds automatically
      but ``to_api_dict()`` omits when unset.
    - Strips ``id`` if it is an empty string (items of list fields often have ``id: ""``).
    - Recurses into ``properties`` and ``items``.
    """
    result = {}
    for key, value in field.items():
        if ignore_origin and key in _NOISE_KEYS:
            continue
        if key in _OMIT_IF_NONE and value is None:
            continue
        if key in _OMIT_IF_EMPTY_STRING and value == "":
            continue
        if key == "properties" and isinstance(value, list):
            result[key] = [normalize_field(prop, ignore_origin=ignore_origin) for prop in value]
        elif key == "items" and isinstance(value, dict):
            result[key] = normalize_field(value, ignore_origin=ignore_origin)
        else:
            result[key] = value
    return result


def fields_equivalent(a: dict, b: dict, *, ignore_origin: bool = False) -> bool:
    return normalize_field(a, ignore_origin=ignore_origin) == normalize_field(b, ignore_origin=ignore_origin)


def find_report_field_in_sections(report_sections: list[dict], field_id: str) -> Optional[dict]:
    for section in report_sections:
        for field in section.get("fields", []):
            if isinstance(field, dict) and field.get("id") == field_id:
                return field
    return None


@pytest.fixture
def reptor():
    instance = Reptor(
        server=os.environ.get("SYSREPTOR_SERVER"),
        token=os.environ.get("SYSREPTOR_API_TOKEN"),
    )
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        instance._config._raw_config["insecure"] = True
        instance._config._raw_config["cli"] = {"insecure": True}
    return instance


@pytest.fixture
def project_design_api(reptor):
    return reptor.api.project_designs


_SEVERITY_FIELD = ProjectDesignField(
    {
        "id": "severity",
        "type": "enum",
        "label": "Severity",
        "required": True,
        "default": None,
        "choices": [
            {"value": "critical", "label": "Critical"},
            {"value": "high", "label": "High"},
            {"value": "medium", "label": "Medium"},
            {"value": "low", "label": "Low"},
            {"value": "info", "label": "Info"},
        ],
    }
)

_LIST_FIELD = ProjectDesignField(
    {
        "id": "affected_components",
        "type": "list",
        "label": "Affected Components",
        "required": False,
        "items": {
            "type": "string",
            "label": "Component",
            "default": "TODO: affected component",
            "required": True,
        },
    }
)

_REPORT_SECTIONS = [
    {
        "id": "default",
        "label": "Default",
        "fields": [
            {
                "id": "title",
                "type": "string",
                "label": "Report Title",
                "required": True,
                "default": "",
                "spellcheck": True,
            }
        ],
    }
]


@pytest.fixture
def private_design(project_design_api):
    design = project_design_api.create_project_design(
        name="Field Definition Integration Test",
        scope="private",
    )
    try:
        design = project_design_api.update_project_design(
            project_design_id=design.id,
            finding_fields=[_SEVERITY_FIELD, _LIST_FIELD],
            report_sections=_REPORT_SECTIONS,
        )
        yield design
    finally:
        project_design_api.delete_project_design(project_design_id=design.id)


@pytest.mark.integration
class TestIntegrationProjectDesignFields:
    def test_api_response_has_no_top_level_report_fields(self, project_design_api, private_design):
        raw = get_raw_design(project_design_api, private_design.id)
        assert "report_fields" not in raw
        assert "report_sections" in raw
        assert isinstance(raw["finding_fields"], list)

    def test_finding_fields_payload_type_is_string(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        assert len(design.finding_fields) > 0
        for field in design.finding_fields:
            api_dict = field.to_api_dict()
            assert isinstance(api_dict["type"], str)

    def test_finding_fields_no_spurious_keys_on_string_field(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        title_field = next(f for f in design.finding_fields if f.id == "title")
        result = title_field.to_api_dict()
        assert "choices" not in result
        assert "suggestions" not in result
        assert "items" not in result
        assert "properties" not in result

    def test_finding_fields_null_defaults_not_empty_string(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        severity_field = next((f for f in design.finding_fields if f.id == "severity"), None)
        assert severity_field is not None, "Design must have a severity field"
        assert severity_field.default is None
        assert severity_field.to_api_dict()["default"] is None

    def test_finding_fields_roundtrip_preserves_definitions(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        before = get_raw_design(project_design_api, private_design.id)["finding_fields"]

        project_design_api.update_project_design(
            project_design_id=private_design.id,
            finding_fields=design.finding_fields,
        )

        after = get_raw_design(project_design_api, private_design.id)["finding_fields"]
        assert len(after) == len(before)
        for before_field, after_field in zip(before, after):
            assert before_field["id"] == after_field["id"]
            assert fields_equivalent(before_field, after_field, ignore_origin=True)

    def test_finding_fields_enum_choices_roundtrip(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        severity_field = next((f for f in design.finding_fields if f.id == "severity"), None)
        assert severity_field is not None, "Design must have a severity field"

        before_choices = severity_field.choices
        project_design_api.update_project_design(
            project_design_id=private_design.id,
            finding_fields=design.finding_fields,
        )

        raw = get_raw_design(project_design_api, private_design.id)
        after_field = field_by_id(raw["finding_fields"], "severity")
        assert after_field["choices"] == before_choices

    def test_finding_fields_list_items_roundtrip(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        list_field = next((f for f in design.finding_fields if f.type == "list"), None)
        assert list_field is not None, "Design must have a list field"

        before_items = list_field.to_api_dict()["items"]
        project_design_api.update_project_design(
            project_design_id=private_design.id,
            finding_fields=design.finding_fields,
        )

        raw = get_raw_design(project_design_api, private_design.id)
        after_field = field_by_id(raw["finding_fields"], list_field.id)
        assert fields_equivalent({"items": before_items}, {"items": after_field["items"]}, ignore_origin=True)

    def test_finding_fields_object_properties_roundtrip(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        updated_fields = list(design.finding_fields)
        updated_fields.append(ProjectDesignField({
            "id": "test_object",
            "type": "object",
            "label": "Test Object",
            "origin": "custom",
            "required": True,
            "properties": [
                {"id": "nested", "type": "string", "label": "Nested", "origin": "custom", "required": True, "spellcheck": False},
            ],
        }))

        project_design_api.update_project_design(
            project_design_id=private_design.id,
            finding_fields=updated_fields,
        )

        raw = get_raw_design(project_design_api, private_design.id)
        object_field = field_by_id(raw["finding_fields"], "test_object")
        assert object_field is not None
        assert len(object_field["properties"]) == 1
        assert object_field["properties"][0]["id"] == "nested"

    def test_finding_fields_number_field_preserves_constraints(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        updated_fields = list(design.finding_fields)
        updated_fields.append(ProjectDesignField({
            "id": "test_number",
            "type": "number",
            "label": "Test Number",
            "origin": "custom",
            "default": None,
            "minimum": 1,
            "maximum": 10,
            "required": False,
        }))

        project_design_api.update_project_design(
            project_design_id=private_design.id,
            finding_fields=updated_fields,
        )

        raw = get_raw_design(project_design_api, private_design.id)
        number_field = field_by_id(raw["finding_fields"], "test_number")
        assert number_field["minimum"] == 1
        assert number_field["maximum"] == 10

    def test_finding_fields_boolean_default_roundtrip(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        updated_fields = list(design.finding_fields)
        updated_fields.append(ProjectDesignField({
            "id": "test_boolean",
            "type": "boolean",
            "label": "Test Boolean",
            "origin": "custom",
            "default": False,
            "required": False,
        }))

        project_design_api.update_project_design(
            project_design_id=private_design.id,
            finding_fields=updated_fields,
        )

        raw = get_raw_design(project_design_api, private_design.id)
        boolean_field = field_by_id(raw["finding_fields"], "test_boolean")
        assert boolean_field["default"] is False
        assert boolean_field["type"] == "boolean"

    def test_report_fields_update_changes_label(self, project_design_api, private_design):
        design = project_design_api.get_project_design(project_design_id=private_design.id)
        title_field = next((f for f in design.report_fields if f.id == "title"), None)
        assert title_field is not None, "Design must have a title report field"

        updated_title = ProjectDesignField({
            "id": "title",
            "type": "string",
            "label": "Updated Report Title Label",
            "origin": title_field.origin,
            "default": title_field.default,
            "required": title_field.required,
            "spellcheck": title_field.spellcheck,
        })

        project_design_api.update_project_design(
            project_design_id=private_design.id,
            report_fields=[updated_title],
        )

        raw = get_raw_design(project_design_api, private_design.id)
        report_title = find_report_field_in_sections(raw["report_sections"], "title")
        assert report_title is not None
        assert report_title["label"] == "Updated Report Title Label"
