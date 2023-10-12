import re
from typing import Union

from requests.exceptions import HTTPError
from reptor.models.Finding import Finding
from reptor.models.Section import Section

from reptor.models.Base import ProjectFieldTypes
from reptor.lib.plugins.Base import Base

try:
    import deepl
except ImportError:
    deepl = None


class Translate(Base):
    """ """

    meta = {
        "name": "Translate",
        "summary": "Translate Projects to other languages via Deepl",
    }

    PREDEFINED_SKIP_FIELDS = [
        "affected_components",
        "references",
    ]
    TRANSLATE_DATA_TYPES = [
        ProjectFieldTypes.string.value,
        ProjectFieldTypes.markdown.value,
    ]
    DEEPL_FROM = [
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
    DEEPL_TO = [
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.from_lang = kwargs.get("from")
        self.to_lang = kwargs["to"]
        self.dry_run = kwargs.get("dry_run")
        self.chars_count_to_translate = 0
        try:
            self.skip_fields = kwargs.get("skip_fields", "").split(",") or getattr(
                self, "skip_fields"
            )
        except AttributeError:
            self.skip_fields = list()
        try:
            self.skip_fields.extend(self.PREDEFINED_SKIP_FIELDS)
        except TypeError:
            raise TypeError(f"skip_fields should be list.")
        if not hasattr(self, "deepl_api_token"):
            self.deepl_api_token = ""

        try:
            if not self.deepl_api_token:
                # TODO error msg might propose a conf command for interactive configuration
                raise AttributeError("No Deepl API token found.")
            if not deepl:
                raise ModuleNotFoundError(
                    'deepl library not found. Install plugin requirements with "pip3 install reptor[translate]'
                )
            self.deepl_translator = deepl.Translator(self.deepl_api_token)
        except (AttributeError, ModuleNotFoundError) as e:
            if not self.dry_run:
                raise e

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--from",
            metavar="LANGUAGE_CODE",
            help="Language code of source language",
            choices=cls.DEEPL_FROM,
            action="store",
            default=None,
        )
        parser.add_argument(
            "--to",
            metavar="LANGUAGE_CODE",
            help="Language code of dest language",
            choices=cls.DEEPL_TO,
            action="store",
            default=None,
        )
        parser.add_argument(
            "--skip-fields",
            metavar="FIELDS",
            help="Report and Finding fields, comma-separated",
            action="store",
            default="",
        )

        # Currently supported: Deepl
        # parser.add_argument(
        #    "--translator",
        #    help="Translator service to use",
        #    choices=["deepl"],
        #    default="deepl",
        # )
        parser.add_argument(
            "--dry-run",
            help="Do not translate, count characters to be translated and checks Deepl quota",
            action="store_true",
        )

    def _translate(self, text: str) -> str:
        if not re.search("[a-zA-Z]", text):
            return text

        self.chars_count_to_translate += len(text)

        result = self.deepl_translator.translate_text(
            text,
            source_lang=self.from_lang,  # Can be None
            target_lang=self.to_lang,
            preserve_formatting=True,
        )
        return result.text  # type: ignore

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
            self.reptor.api.projects.switch_project(to_project_id)

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
        self._log_deepl_usage()
        self.success(f"Project translated{' (dry run)' if self.dry_run else ''}.")
        self.display(
            "We recommend to check quality of the translation, or to add a note that the report was "
            "translated by a machine."
        )

    def _log_deepl_usage(self):
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
