import re
import typing

from requests.exceptions import HTTPError

from reptor.api.models import Finding, FindingData
from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.lib.plugins.Base import Base

try:
    import deepl
except ImportError:
    deepl = None


class Translate(Base):
    """ """

    meta = {
        "name": "Translate",
        "summary": "Translate Projects and Templates to other languages",
    }

    SKIP_FINDING_FIELDS = [
        "cvss",
        "affected_components",
        "references",
        "owasp_top10_2021",
        "wstg_category",
        "retest_status",
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
        self.to_lang = kwargs.get("to")
        self.translator = kwargs.get("translator")
        self.dry_run = kwargs.get("dry_run")
        self.deepl_translator = None
        self.chars_count_to_translate = 0

        if hasattr(self, "skip_finding_fields"):  # from user config
            try:
                self.SKIP_FINDING_FIELDS.extend(self.skip_finding_fields)
            except TypeError:
                raise TypeError(
                    f"Error in user config: skip_finding_fields should be list."
                )

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        parser.add_argument(
            "-from",
            "--from",
            metavar="LANGUAGE_CODE",
            help="Language code of source language",
            choices=cls.DEEPL_FROM,
            action="store",
            default=None,
        )
        parser.add_argument(
            "-to",
            "--to",
            metavar="LANGUAGE_CODE",
            help="Language code of dest language",
            choices=cls.DEEPL_TO,
            action="store",
            default=None,
        )

        parser.add_argument(
            "-translator",
            "--translator",
            help="Translator service to use",
            choices=["deepl"],
            default="deepl",
        )
        parser.add_argument(
            "-dry-run",
            "--dry-run",
            help="Do not translate, count characters to be translated and checks Deepl quota",
            action="store_true",
        )

    def _set_deepl_translator(self) -> None:
        if not deepl:
            raise ModuleNotFoundError(
                'deepl library not found. Install with "pip3 install reptor[deepl]'
            )

        try:
            self.deepl_translator = deepl.Translator(self.deepl_api_token)
        except AttributeError:
            # TODO error msg might propose a conf command for interactive configuration
            raise AttributeError("No Deepl API token found.")

    def _translate(self, text: str) -> str:
        self._set_deepl_translator()

        if not re.search("[a-zA-Z]", text):
            return text

        self.chars_count_to_translate += len(text)
        result = self.deepl_translator.translate_text(
            text,
            source_lang=self.from_lang,  # Can be None
            target_lang=self.to_lang,
            preserve_formatting=True,
        )
        return result.text

    def _translate_finding(self, finding: Finding) -> Finding:
        translated_finding = Finding()
        translated_finding.id = finding.id
        translated_finding.data = FindingData()
        finding_data_dict = finding.data.__dict__
        for key in self.SKIP_FINDING_FIELDS:
            finding_data_dict.pop(key, None)

        translated_finding.data = FindingData(self._translate_fields(finding_data_dict))
        return translated_finding

    def _translate_fields(
        self, fields: typing.Collection, root: bool = True
    ) -> typing.Collection:
        """Recursive function to translate nested fields"""
        if isinstance(fields, str):
            return self._translate(fields)
        elif isinstance(fields, dict):
            for key, value in fields.items():
                fields[key] = self._translate_fields(value, root=False)
        elif isinstance(fields, list):
            fields = [self._translate_fields(f) for f in fields]
        return fields

    def _dry_run_translate(self, text: str) -> str:
        self.chars_count_to_translate += len(text)
        return text

    def _translate_project(self) -> None:
        # TODO also translate reptor sections
        # TODO this method might be simplified
        if self.dry_run:
            self._translate = self._dry_run_translate
        self.display(f"Translating project name{' (dry run)' if self.dry_run else ''}.")
        from_projects_api: ProjectsAPI = ProjectsAPI(reptor=self.reptor)
        from_project = from_projects_api.get_project()
        from_project_name = from_project.name
        to_project_title = self._translate(from_project_name)

        self.display(f"Duplicating project{' (dry run)' if self.dry_run else ''}.")
        if not self.dry_run:
            to_project_id = from_projects_api.duplicate().id
            self.display(
                f"Updating project metadata{' (dry run)' if self.dry_run else ''}."
            )
            self.projects_api: ProjectsAPI = ProjectsAPI(
                reptor=self.reptor, project_id=to_project_id
            )
            try:
                sysreptor_language_code = self._get_sysreptor_language_code(
                    self.to_lang
                )
                self.projects_api.update_project(
                    {"language": sysreptor_language_code, "name": to_project_title}
                )
            except HTTPError as e:
                self.warning(f"Error updating project language: {e.response.text}")
        else:
            self.projects_api: ProjectsAPI = ProjectsAPI(
                reptor=self.reptor, project_id=from_project.id
            )

        self.display(f"Translating findings{' (dry run)' if self.dry_run else ''}.")
        findings = self.projects_api.get_findings()
        for finding in findings:
            translated_finding = self._translate_finding(finding)
            try:
                self.projects_api.update_finding(
                    translated_finding.id, {"data": translated_finding.data.__dict__}
                )
            except HTTPError as e:
                self.warning(
                    f"Error updating finding {translated_finding.id}: {e.response.text}"
                )

        try:
            self._set_deepl_translator()
        except (AttributeError, ModuleNotFoundError):
            # Cannot get deeply translator, do not query quota.
            return

        self.display(
            f"Translated {self.chars_count_to_translate} characters{' (dry run)' if self.dry_run else ''}."
        )
        usage = self.deepl_translator.get_usage()
        if usage.any_limit_reached:
            self.warning("Deepl transaction limit reached.")
        if usage.character.valid:
            self.display(
                f"Deepl usage: {usage.character.count} of {usage.character.limit} characters"
            )

    def _get_sysreptor_language_code(self, language_code) -> str:
        enabled_language_codes = self.projects_api.get_enabled_language_codes()
        matched_lcs = [
            enabled_lc
            for enabled_lc in enabled_language_codes
            if enabled_lc.lower().startswith(language_code[:2].lower())
        ]
        if not matched_lcs:
            return enabled_language_codes[0]
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
