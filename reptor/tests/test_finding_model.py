import json
from copy import deepcopy

import pytest

from reptor.models.Finding import (
    FindingData,
    FindingDataField,
    FindingDataRaw,
    FindingRaw,
)
from reptor.models.Project import ProjectDesign


class TestFindingModelParsing:
    example_design_with_finding_fields_only = """
    {"finding_fields":{"cvss":{"type":"cvss","label":"CVSS","origin":"core","default":"n/a","required":true},"title":{"type":"string","label":"Title","origin":"core","default":"TODO: Finding Title","required":true,"spellcheck":true},"date_field":{"type":"date","label":"Date Field","origin":"custom","default":null,"required":true},"enum_field":{"type":"enum","label":"Enum Field","origin":"custom","choices":[{"label":"Enum Value 1","value":"enum_val_1"},{"label":"Enum Value 2","value":"enum_val_2"},{"label":"Enum Value 3","value":"enum_val_"}],"default":null,"required":true},"list_field":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"enum_in_object":{"type":"enum","label":"Enum in Object","origin":"custom","choices":[{"label":"Enum in Obj 1","value":"enum_in_obj_1"},{"label":"Enum in Obj 2","value":"enum_in_obj_2"},{"label":"Enum in Obj 3","value":"enum_in_obj_3"}],"default":null,"required":true}}},"label":"List Field","origin":"custom","required":true},"user_field":{"type":"user","label":"User Field","origin":"custom","required":true},"number_field":{"type":"number","label":"Number Field","origin":"custom","default":null,"required":true},"object_field":{"type":"object","label":"Object Field","origin":"custom","properties":{"list_in_object":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"List in Object","origin":"custom","required":true}}},"boolean_field":{"type":"boolean","label":"Boolean Field","origin":"custom","default":null},"combobox_field":{"type":"combobox","label":"Combobox Field","origin":"custom","default":null,"required":true,"suggestions":["Combobox Value 1","Combobox Value 2","Combobox Value 3"]},"markdown_field":{"type":"markdown","label":"Markdown Field","origin":"custom","default":null,"required":true}}}"""

    example_finding = """
    {
        "id": "d3658ee5-2d43-40f6-9b97-1b98480afe78",
        "created": "2023-07-16T20:07:36.213385Z",
        "updated": "2023-07-16T20:08:59.749591Z",
        "project": "a4b4b630-fc78-452d-b348-d362b69c2449",
        "project_type": "2970149f-e11d-420a-8a5d-25b5fda14e33",
        "language": "en-US",
        "lock_info": null,
        "template": null,
        "assignee": {
            "id": "788dcb76-9928-46fc-87ba-7043708f1bc0",
            "username": "demo-fTaIO4fj",
            "name": "",
            "title_before": null,
            "first_name": "",
            "middle_name": null,
            "last_name": "",
            "title_after": null,
            "is_active": true
        },
        "status": "in-progress",
        "data": {
            "cvss": "n/a",
            "title": "My Title",
            "date_field": "2023-07-03",
            "enum_field": "enum_val_2",
            "list_field": [
                {
                    "enum_in_object": "enum_in_obj_2"
                },
                {
                    "enum_in_object": "enum_in_obj_3"
                }
            ],
            "user_field": "788dcb76-9928-46fc-87ba-7043708f1bc0",
            "number_field": 1337.0,
            "object_field": {
                "list_in_object": [
                    "My String in List in Object",
                    "Other String in List in Object"
                ]
            },
            "boolean_field": true,
            "combobox_field": "Combobox Value 2",
            "markdown_field": "My Markdown"
        }
    }"""

    def test_finding_data(self):
        json_example = json.loads(self.example_finding)
        finding_raw = FindingRaw(json_example)
        project_design = ProjectDesign(
            json.loads(self.example_design_with_finding_fields_only)
        )
        finding_data = FindingData(project_design.finding_fields, finding_raw.data)
        assert finding_data.boolean_field.name == "boolean_field"
        assert finding_data.boolean_field.type == "boolean"
        assert finding_data.boolean_field.value == True

        assert finding_data.combobox_field.name == "combobox_field"
        assert finding_data.combobox_field.type == "combobox"
        assert finding_data.combobox_field.value == "Combobox Value 2"

        assert finding_data.cvss.name == "cvss"
        assert finding_data.cvss.type == "cvss"
        assert finding_data.cvss.value == "n/a"

        assert finding_data.date_field.name == "date_field"
        assert finding_data.date_field.type == "date"
        assert finding_data.date_field.value == "2023-07-03"

        assert finding_data.enum_field.name == "enum_field"
        assert finding_data.enum_field.type == "enum"
        assert finding_data.enum_field.value == "enum_val_2"

        assert finding_data.list_field.name == "list_field"
        assert finding_data.list_field.type == "list"
        assert isinstance(finding_data.list_field.value, list)
        assert isinstance(finding_data.list_field.value[0], FindingDataField)
        assert finding_data.list_field.value[0].type == "object"
        assert isinstance(finding_data.list_field.value[0].value, dict)
        assert isinstance(
            finding_data.list_field.value[0].value["enum_in_object"], FindingDataField
        )
        assert finding_data.list_field.value[0].value["enum_in_object"].type == "enum"
        assert (
            finding_data.list_field.value[0].value["enum_in_object"].value
            == "enum_in_obj_2"
        )
        assert finding_data.object_field.name == "object_field"
        assert finding_data.object_field.type == "object"
        assert isinstance(finding_data.object_field.value, dict)
        assert isinstance(
            finding_data.object_field.value["list_in_object"], FindingDataField
        )
        assert finding_data.object_field.value["list_in_object"].type == "list"
        assert isinstance(finding_data.object_field.value["list_in_object"].value, list)
        assert isinstance(
            finding_data.object_field.value["list_in_object"].value[0], FindingDataField
        )
        assert (
            finding_data.object_field.value["list_in_object"].value[0].type == "string"
        )
        assert (
            finding_data.object_field.value["list_in_object"].value[0].value
            == "My String in List in Object"
        )

        assert finding_data.to_json() == json_example["data"]

        # Try to set attributes
        finding_data.enum_field.value = "enum_val_1"
        assert finding_data.enum_field.value == "enum_val_1"
        with pytest.raises(ValueError):
            finding_data.enum_field.value = "invalid_value"

        finding_data.boolean_field.value = False
        assert finding_data.boolean_field.value == False
        with pytest.raises(ValueError):
            finding_data.boolean_field.value = "invalid_value"

        finding_data.combobox_field.value = "Combobox Value 1"
        assert finding_data.combobox_field.value == "Combobox Value 1"
        with pytest.raises(ValueError):
            finding_data.combobox_field.value = True

        finding_data.date_field.value = "2005-01-01"
        assert finding_data.date_field.value == "2005-01-01"
        with pytest.raises(ValueError):
            finding_data.date_field.value = "2002-01-32"

        new_list = deepcopy(finding_data.list_field.value)
        new_list[0].value["enum_in_object"].value = "enum_in_obj_1"
        finding_data.list_field.value = new_list
        assert finding_data.list_field.value == new_list
        with pytest.raises(ValueError):
            # ValueError due to invalid enum
            new_list[0].value["enum_in_object"].value = "invalid_value"
        with pytest.raises(ValueError):
            finding_data.list_field.value = "invalid_value"
        with pytest.raises(ValueError):
            finding_data.list_field.value = [new_list[0], "invalid_value"]
        with pytest.raises(ValueError):
            finding_data.list_field.value = [new_list[0], finding_data.combobox_field]

        new_object = deepcopy(finding_data.object_field.value)
        new_object["list_in_object"].value[0].value = "My new String in List in Object"
        finding_data.object_field.value = new_object
        assert finding_data.object_field.value == new_object
        with pytest.raises(ValueError):
            # ValueError due to invalid string
            new_object["list_in_object"].value[0].value = 1
        with pytest.raises(ValueError):
            finding_data.object_field.value = "invalid_value"
        with pytest.raises(ValueError):
            finding_data.object_field.value = [
                new_object["list_in_object"],
                "invalid_value",
            ]
        with pytest.raises(ValueError):
            finding_data.object_field.value = [
                new_object["list_in_object"],
                finding_data.combobox_field,
            ]

        with pytest.raises(ValueError):
            finding_data.number_field.value = "invalid_value"

        finding_data.user_field.value = "3cb580bd-131b-48f0-9e37-b405e2ab53b8"
        with pytest.raises(ValueError):
            finding_data.user_field.value = "invalid_value"

    def test_finding_raw_parsing(self):
        api_test_data = json.loads(self.example_finding)
        finding = FindingRaw(api_test_data)
        assert finding.id == "d3658ee5-2d43-40f6-9b97-1b98480afe78"
        assert finding.language == "en-US"
        assert finding.project_type == "2970149f-e11d-420a-8a5d-25b5fda14e33"
        assert isinstance(finding.assignee, dict)
        assert isinstance(finding.data, FindingDataRaw)
        assert finding.data.cvss == "n/a"
        assert finding.data.title == "My Title"
        assert finding.data.date_field == "2023-07-03"
        assert finding.data.enum_field == "enum_val_2"
        assert isinstance(finding.data.list_field, list)
        assert len(finding.data.list_field) == 2
        assert finding.data.list_field[0] == {"enum_in_object": "enum_in_obj_2"}
        assert finding.data.user_field == "788dcb76-9928-46fc-87ba-7043708f1bc0"
        assert finding.data.number_field == 1337.0
        assert isinstance(finding.data.number_field, float)
        assert isinstance(finding.data.object_field, dict)
        assert "list_in_object" in finding.data.object_field
        assert len(finding.data.object_field["list_in_object"]) == 2
        assert (
            finding.data.object_field["list_in_object"][0]
            == "My String in List in Object"
        )
        assert finding.data.boolean_field == True
        assert finding.data.combobox_field == "Combobox Value 2"
        assert finding.data.markdown_field == "My Markdown"
