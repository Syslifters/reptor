import json
from copy import deepcopy

import pytest

from reptor.api.manager import APIManager
from reptor.lib.reptor import Reptor
from reptor.models.Finding import Finding, FindingRaw
from reptor.models.ProjectDesign import ProjectDesign

from ..Translate import Translate


class TestTranslate:
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
    example_design_with_finding_fields_only = """
    {"finding_fields":{"cvss":{"type":"cvss","label":"CVSS","origin":"core","default":"n/a","required":true},"title":{"type":"string","label":"Title","origin":"core","default":"TODO: Finding Title","required":true,"spellcheck":true},"date_field":{"type":"date","label":"Date Field","origin":"custom","default":null,"required":true},"enum_field":{"type":"enum","label":"Enum Field","origin":"custom","choices":[{"label":"Enum Value 1","value":"enum_val_1"},{"label":"Enum Value 2","value":"enum_val_2"},{"label":"Enum Value 3","value":"enum_val_"}],"default":null,"required":true},"list_field":{"type":"list","items":{"type":"object","label":"","origin":"custom","properties":{"enum_in_object":{"type":"enum","label":"Enum in Object","origin":"custom","choices":[{"label":"Enum in Obj 1","value":"enum_in_obj_1"},{"label":"Enum in Obj 2","value":"enum_in_obj_2"},{"label":"Enum in Obj 3","value":"enum_in_obj_3"}],"default":null,"required":true}}},"label":"List Field","origin":"custom","required":true},"user_field":{"type":"user","label":"User Field","origin":"custom","required":true},"number_field":{"type":"number","label":"Number Field","origin":"custom","default":null,"required":true},"object_field":{"type":"object","label":"Object Field","origin":"custom","properties":{"list_in_object":{"type":"list","items":{"type":"string","label":"","origin":"custom","default":null,"required":true,"spellcheck":false},"label":"List in Object","origin":"custom","required":true}}},"boolean_field":{"type":"boolean","label":"Boolean Field","origin":"custom","default":null},"combobox_field":{"type":"combobox","label":"Combobox Field","origin":"custom","default":null,"required":true,"suggestions":["Combobox Value 1","Combobox Value 2","Combobox Value 3"]},"markdown_field":{"type":"markdown","label":"Markdown Field","origin":"custom","default":null,"required":true}}}"""

    @pytest.fixture(autouse=True)
    def setUp(self):
        class Translator:
            def translate_text(self, text, **kwargs):
                class Result:
                    def __init__(self, text):
                        self.text = text

                return Result(f"Translated: {text}")

        reptor = Reptor()
        reptor._config._raw_config[
            "project_id"
        ] = "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e"
        reptor._api = APIManager(reptor=reptor)
        self.translate = Translate(reptor=reptor, to="EN", dry_run=True)
        self.translate.deepl_translator = Translator()

        finding_raw = FindingRaw(json.loads(self.example_finding))
        project_design = ProjectDesign(
            json.loads(self.example_design_with_finding_fields_only)
        )
        self.finding = Finding(
            finding_raw, project_design, raise_on_unknown_fields=True
        )

    def test_translate(self):
        assert self.translate.chars_count_to_translate == 0
        assert self.translate._dry_run_translate("12345") == "12345"
        assert self.translate.chars_count_to_translate == 5

        text = "Hello World"
        assert self.translate._translate(text) == f"Translated: {text}"
        assert self.translate.chars_count_to_translate == 5 + len(text)
        assert self.translate._translate("123") == f"123"
        assert self.translate.chars_count_to_translate == 5 + len(text)

        self.translate.skip_fields = ["title"]
        translated_finding = self.translate._translate_section(deepcopy(self.finding))

        # Fields that should be translated
        assert (
            translated_finding.data.markdown_field.value
            == f"Translated: {self.finding.data.markdown_field.value}"
        )
        assert (
            translated_finding.data.object_field.value["list_in_object"].value[0].value
            == f"Translated: {self.finding.data.object_field.value['list_in_object'].value[0].value}"
        )

        # Fields not translated due to skip_fields
        assert translated_finding.data.title.value == self.finding.data.title.value

        # Fields that should not be translated
        assert (
            translated_finding.data.combobox_field.value
            == self.finding.data.combobox_field.value
        )
        assert translated_finding.data.cvss.value == self.finding.data.cvss.value
        assert (
            translated_finding.data.enum_field.value
            == self.finding.data.enum_field.value
        )
        assert (
            translated_finding.data.list_field.value[0].value["enum_in_object"].value
            == self.finding.data.list_field.value[0].value["enum_in_object"].value
        )

    def test_language_code_mapping(self):
        class Reptor:
            class Api:
                class Projects:
                    def get_enabled_language_codes(self) -> list:
                        return ["en-US", "de-DE", "es-ES", "fr-FR", "de-XX"]

                projects = Projects()

            api = Api()

        self.translate.reptor = Reptor()
        assert self.translate._get_sysreptor_language_code("EN") == "en-US"
        assert self.translate._get_sysreptor_language_code("EN-GB") == "en-US"
        assert self.translate._get_sysreptor_language_code("EN-US") == "en-US"

        assert self.translate._get_sysreptor_language_code("DE") == "de-DE"
        assert self.translate._get_sysreptor_language_code("DE-xX") == "de-XX"
        assert self.translate._get_sysreptor_language_code("ES") == "es-ES"
        assert self.translate._get_sysreptor_language_code("FR") == "fr-FR"

        assert self.translate._get_sysreptor_language_code("invalid") == ""
