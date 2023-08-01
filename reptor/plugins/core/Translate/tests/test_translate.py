import json
import unittest
from copy import deepcopy

from reptor.api.manager import APIManager
from reptor.api.models import Finding, FindingRaw, ProjectDesign
from reptor.lib.reptor import Reptor

from ..Translate import Translate


class TranslateTests(unittest.TestCase):
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

    def setUp(self) -> None:
        reptor = Reptor()
        reptor._api = APIManager(reptor=reptor)
        self.translate = Translate(reptor=reptor, to="EN", dry_run=True)

        finding_raw = FindingRaw(json.loads(self.example_finding))
        project_design = ProjectDesign(json.loads(
            self.example_design_with_finding_fields_only))
        self.finding = Finding(project_design, finding_raw)

        return super().setUp()

    def test_translate(self):
        self.assertEqual(self.translate.chars_count_to_translate, 0)
        self.assertEqual(self.translate._dry_run_translate('12345'), '12345')
        self.assertEqual(self.translate.chars_count_to_translate, 5)

        self.translate.deepl_translator.translate_text = self._translate
        text = "Hello World"
        self.assertEqual(self.translate._translate(
            text), f"Translated: {text}")
        self.assertEqual(self.translate.chars_count_to_translate, 5+len(text))
        self.assertEqual(self.translate._translate("123"), f"123")
        self.assertEqual(self.translate.chars_count_to_translate, 5+len(text))

        translated_finding = self.translate._translate_section(
            deepcopy(self.finding))

        # Fields that should be translated
        self.assertEqual(
            translated_finding.data.markdown_field.value,
            f"Translated: {self.finding.data.markdown_field.value}")
        self.assertEqual(
            translated_finding.data.title.value,
            f"Translated: {self.finding.data.title.value}")
        self.assertEqual(
            translated_finding.data.object_field.value['list_in_object'].value[0].value,
            f"Translated: {self.finding.data.object_field.value['list_in_object'].value[0].value}")

        # Fields that should not be translated
        self.assertEqual(
            translated_finding.data.combobox_field.value,
            f"{self.finding.data.combobox_field.value}")
        self.assertEqual(
            translated_finding.data.cvss.value,
            f"{self.finding.data.cvss.value}")
        self.assertEqual(
            translated_finding.data.enum_field.value,
            f"{self.finding.data.enum_field.value}")
        self.assertEqual(
            translated_finding.data.list_field.value[0].value['enum_in_object'].value,
            f"{self.finding.data.list_field.value[0].value['enum_in_object'].value}")
        pass

    def test_language_code_mapping(self):
        self.translate.reptor.api.projects.get_enabled_language_codes = self._get_enabled_language_codes
        self.assertEqual(
            self.translate._get_sysreptor_language_code("EN"), "en-US")
        self.assertEqual(
            self.translate._get_sysreptor_language_code("EN-GB"), "en-US")
        self.assertEqual(
            self.translate._get_sysreptor_language_code("EN-US"), "en-US")

        self.assertEqual(
            self.translate._get_sysreptor_language_code("DE"), "de-DE")
        self.assertEqual(
            self.translate._get_sysreptor_language_code("DE-xX"), "de-XX")
        self.assertEqual(
            self.translate._get_sysreptor_language_code("ES"), "es-ES")
        self.assertEqual(
            self.translate._get_sysreptor_language_code("FR"), "fr-FR")

        self.assertEqual(
            self.translate._get_sysreptor_language_code("invalid"), "")

    def _get_enabled_language_codes(self) -> list:
        return ["en-US", "de-DE", "es-ES", "fr-FR", "de-XX"]

    def _translate(self, text, **kwargs):
        class Result:
            def __init__(self, text):
                self.text = text
        return Result(f"Translated: {text}")
