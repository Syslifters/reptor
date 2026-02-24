import argparse
import re
from typing import Union

from requests.exceptions import HTTPError

from reptor.lib.plugins.Base import Base
from reptor.models.Base import ProjectFieldTypes
from reptor.models.Finding import Finding
from reptor.models.Section import Section
from reptor.models.UserConfig import UserConfig

try:
    import deepl
except ImportError:
    deepl = None

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None


class Translate(Base):
    """ """

    meta = {
        "name": "Translate",
        "summary": "Translate Projects to other languages via Deepl or Azure OpenAI",
    }

    PREDEFINED_SKIP_FIELDS = [
        "affected_components",
        "references",
    ]
    TRANSLATE_DATA_TYPES = [
        ProjectFieldTypes.string.value,
        ProjectFieldTypes.markdown.value,
    ]
    LANG_FROM = [
        "BG",
        "CS",
        "DA",
        "DE",
        "EL",
        "EN",
        "ES",
        "ET",
        "FI",
        "FR",
        "HU",
        "ID",
        "IT",
        "JA",
        "KO",
        "LT",
        "LV",
        "NB",
        "NL",
        "PL",
        "PT",
        "RO",
        "RU",
        "SK",
        "SL",
        "SV",
        "TR",
        "UK",
        "ZH",
    ]
    LANG_TO = [
        "BG",
        "CS",
        "DA",
        "DE",
        "EL",
        "EN",
        "EN-GB",
        "EN-US",
        "ES",
        "ET",
        "FI",
        "FR",
        "HU",
        "ID",
        "IT",
        "JA",
        "KO",
        "LT",
        "LV",
        "NB",
        "NL",
        "PL",
        "PT",
        "PT-BR",
        "PT-PT",
        "RO",
        "RU",
        "SK",
        "SL",
        "SV",
        "TR",
        "UK",
        "ZH",
    ]
    TRANSLATION_SERVICES = ["deepl", "azure"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.from_lang = kwargs.get("from")
        self.to_lang = kwargs["to"]
        self.dry_run = kwargs.get("dry_run")
        self.translation_service = kwargs.get("service") or kwargs.get("translation_service", "deepl")
        self.chars_count_to_translate = 0
        self.skip_fields = kwargs.get("skip_fields", None) or getattr(
            self, "skip_fields", None
        )
        if self.skip_fields:
            self.skip_fields = self.skip_fields.split(",")
        else:
            self.skip_fields = list()
        try:
            self.skip_fields.extend(self.PREDEFINED_SKIP_FIELDS)
        except TypeError:
            raise TypeError("skip_fields should be list.")
        
        if self.translation_service == "deepl":
            if not hasattr(self, "deepl_api_token"):
                self.deepl_api_token = ""
            try:
                if not self.deepl_api_token:
                    raise AttributeError("No Deepl API token found. Try --conf.")
                if not deepl:
                    raise ModuleNotFoundError(
                        'deepl library not found. Install plugin requirements with "pip3 install reptor[translate]'
                    )
                self.deepl_translator = deepl.Translator(self.deepl_api_token)
            except (AttributeError, ModuleNotFoundError) as e:
                if not self.dry_run:
                    raise e
        elif self.translation_service == "azure":
            if not hasattr(self, "azure_api_key"):
                self.azure_api_key = ""
            if not hasattr(self, "azure_resource_name"):
                self.azure_resource_name = ""
            if not hasattr(self, "azure_api_version"):
                self.azure_api_version = ""
            if not hasattr(self, "azure_endpoint"):
                self.azure_endpoint = ""
            if not hasattr(self, "azure_model"):
                self.azure_model = "gpt-4"
            
            try:
                if not self.azure_api_key:
                    raise AttributeError("No Azure API key found. Try --conf.")
                if not self.azure_resource_name:
                    raise AttributeError("No Azure resource name found. Try --conf.")
                if not self.azure_api_version:
                    raise AttributeError("No Azure API version found. Try --conf.")
                if not self.azure_endpoint and not self.azure_resource_name:
                    raise AttributeError("No Azure endpoint or resource name found. Try --conf.")
                if not AzureOpenAI:
                    raise ModuleNotFoundError(
                        'openai library not found. Install with "pip3 install openai'
                    )
                
                endpoint = self.azure_endpoint or f"https://{self.azure_resource_name}.openai.azure.com/"
                
                self.azure_translator = AzureOpenAI(
                    api_key=self.azure_api_key,
                    api_version=self.azure_api_version,
                    azure_endpoint=endpoint,
                )
            except (AttributeError, ModuleNotFoundError) as e:
                if not self.dry_run:
                    raise e

    @property
    def user_config(self):
        return [
            UserConfig(
                name="deepl_api_token",
                friendly_name="Deepl API Token",
                redact_current_value=True,
            ),
            UserConfig(
                name="azure_api_key",
                friendly_name="Azure OpenAI API Key",
                redact_current_value=True,
            ),
            UserConfig(
                name="azure_resource_name",
                friendly_name="Azure Resource Name",
                redact_current_value=False,
            ),
            UserConfig(
                name="azure_api_version",
                friendly_name="Azure API Version (e.g., 2024-02-15-preview)",
                redact_current_value=False,
            ),
            UserConfig(
                name="azure_endpoint",
                friendly_name="Azure Endpoint URL (optional if resource name provided)",
                redact_current_value=False,
            ),
            UserConfig(
                name="azure_model",
                friendly_name="Azure Model Deployment Name (e.g., gpt-4-turbo)",
                redact_current_value=False,
            ),
        ]

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--from",
            metavar="LANGUAGE_CODE",
            help="Language code of source language",
            choices=cls.LANG_FROM,
            action="store",
            default=None,
        )
        parser.add_argument(
            "--to",
            metavar="LANGUAGE_CODE",
            help="Language code of dest language",
            choices=cls.LANG_TO,
            action="store",
            default=None,
        )
        parser.add_argument(
            "--service",
            metavar="SERVICE",
            help="Translation service to use (deepl or azure)",
            choices=cls.TRANSLATION_SERVICES,
            action="store",
            default="deepl",
        )
        parser.add_argument(
            "--skip-fields",
            metavar="FIELDS",
            help="Report and Finding fields, comma-separated",
            action="store",
            default="",
        )
        parser.add_argument(
            "--skipfields",
            metavar="FIELDS",
            help=argparse.SUPPRESS,
            action="store",
            default="",
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            help="Do not translate, count characters to be translated and checks quota",
            action="store_true",
        )
        parser.add_argument(
            "--dryrun",
            dest="dry_run",
            help=argparse.SUPPRESS,
            action="store_true",
        )

    def _translate_deepl(self, text: str) -> str:
        """Translate text using DeepL API."""
        result = self.deepl_translator.translate_text(
            text,
            source_lang=self.from_lang,  # Can be None
            target_lang=self.to_lang,
            preserve_formatting=True,
        )
        return result.text  # type: ignore

    def _translate_azure(self, text: str) -> str:
        """Translate text using Azure OpenAI Chat Model."""
        from_lang = self.from_lang or "auto-detected"
        to_lang = self.to_lang
        
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a professional cybersecurity translator with expertise in penetration testing reports. "
                    f"Translate the following text from {from_lang} to {to_lang} using accurate, formal, and technically precise language appropriate for security documentation. "
                    f"DO NOT translate: code snippets, command syntax, file paths, framework names, tool names, CVE identifiers, or standard names (e.g., HTTP, REST, SQL). "
                    f"Maintain consistent terminology throughout. "
                    f"Preserve all original formatting: headings, markdown, bullet points, numbering, code blocks, tables, and special characters. "
                    f"Return ONLY translated text with no explanations or comments."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
        
        response = self.azure_translator.chat.completions.create(
            model=self.azure_model,
            messages=messages,
            temperature=0.3,
            top_p=0.95,
        )
        
        return response.choices[0].message.content

    def _translate(self, text: str) -> str:
        if not re.search("[a-zA-Z]", text):
            return text

        self.chars_count_to_translate += len(text)

        if self.translation_service == "deepl":
            return self._translate_deepl(text)
        elif self.translation_service == "azure":
            return self._translate_azure(text)
        else:
            raise ValueError(f"Unknown translation service: {self.translation_service}")

    def _translate_section(
        self, section: Union[Finding, Section]
    ) -> Union[Finding, Section]:
        for field in section.data:
            if field.type not in self.TRANSLATE_DATA_TYPES:
                continue
            if field.name in self.skip_fields:
                continue
            if not field.value:
                continue
            field.value = self._translate(field.value)
        return section

    def _dry_run_translate(self, text: str) -> str:
        self.chars_count_to_translate += len(text)
        return text

    def _duplicate_and_update_project(self, project_title: str) -> None:
        self.display(f"Duplicating project{' (dry run)' if self.dry_run else ''}.")
        if not self.dry_run:
            to_project_id = self.reptor.api.projects.duplicate_project().id
            self.display(
                f"Updating project metadata{' (dry run)' if self.dry_run else ''}."
            )
            # Switch project to update duplicated project instead of original
            self.reptor.api.projects.init_project(to_project_id)

            try:
                data = {"name": self._translate(project_title)}
                if sysreptor_language_code := self._get_sysreptor_language_code(
                    self.to_lang
                ):
                    data["language"] = sysreptor_language_code
                self.reptor.api.projects.update_project(data)
            except HTTPError as e:
                self.warning(f"Error updating project: {e.response.text}")
        else:
            self._translate(project_title)  # To count characters

    def _translate_project(self):
        if self.dry_run:
            self._translate = self._dry_run_translate

        project = self.reptor.api.projects.project
        self._duplicate_and_update_project(project_title=project.name)

        self.display(f"Translating findings{' (dry run)' if self.dry_run else ''}.")
        sections = [
            Finding(f, self.reptor.api.project_designs.project_design)
            for f in self.reptor.api.projects.get_findings()
        ] + self.reptor.api.projects.get_sections()
        for section in sections:
            translated_section = self._translate_section(section)
            translated_section_data = translated_section.data.to_dict()
            if not self.dry_run:
                if translated_section.__class__ == Finding:
                    self.reptor.api.projects.update_finding(
                        translated_section.id, {"data": translated_section_data}
                    )
                elif translated_section.__class__ == Section:
                    self.reptor.api.projects.update_section(
                        translated_section.id, {"data": translated_section_data}
                    )

        self.display(
            f"Translated {self.chars_count_to_translate} characters{' (dry run)' if self.dry_run else ''}."
        )
        self._log_service_usage()
        self.success(f"Project translated{' (dry run)' if self.dry_run else ''}.")
        self.display(
            "We recommend to check quality of the translation, or to add a note that the report was "
            "translated by a machine."
        )

    def _log_service_usage(self):
        """Log usage information for the translation service."""
        if self.translation_service == "deepl":
            try:
                usage = self.deepl_translator.get_usage()
                if usage.any_limit_reached:
                    self.warning("Deepl transaction limit reached.")
                if usage.character.valid:
                    self.display(
                        f"Deepl usage: {usage.character.count} of {usage.character.limit} characters"
                    )
            except AttributeError:
                pass
        elif self.translation_service == "azure":
            self.display(
                f"Azure OpenAI: Translated {self.chars_count_to_translate} characters. Translated from {self.from_lang or 'auto-detected language'} to {self.to_lang} using model {self.azure_model}."
            )

    def _get_sysreptor_language_code(self, language_code) -> str:
        enabled_language_codes = self.reptor.api.projects.get_enabled_language_codes()
        matched_lcs = [
            enabled_lc
            for enabled_lc in enabled_language_codes
            if enabled_lc.lower().startswith(language_code[:2].lower())
        ]
        if not matched_lcs:
            return ""
        elif len(matched_lcs) == 1:
            return matched_lcs[0]
        else:
            for matched_lc in matched_lcs:
                if matched_lc.lower() == language_code.lower():
                    return matched_lc
            else:
                return matched_lcs[0]

    def run(self):
        self._translate_project()


loader = Translate