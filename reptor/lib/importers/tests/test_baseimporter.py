import pytest

from reptor.lib.reptor import Reptor
from reptor.models.FindingTemplate import FindingTemplate

from .. import BaseImporter


class TestBaseImporter:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()

    def test_run(self):
        def next_findings_batch(*args, **kwargs):
            return []

        with pytest.raises(AttributeError):
            BaseImporter.BaseImporter(reptor=self.reptor).run()

        BaseImporter.BaseImporter.mapping = {"title": "title"}
        base_importer = BaseImporter.BaseImporter(reptor=self.reptor)
        base_importer.next_findings_batch = next_findings_batch
        base_importer.run()

    def test_next_findings_batch(self):
        with pytest.raises(NotImplementedError):
            BaseImporter.BaseImporter(reptor=self.reptor).next_findings_batch()

    def test_create_and_upload(self):
        class Api:
            class Templates:
                def upload_new_template(self, template, **kwargs):
                    assert template == finding
                    return FindingTemplate(finding_example)

            templates = Templates()

        def convert_old_tools_references(value):
            return value.splitlines()

        finding_example = {
            "id": "e6961177-0582-4dd2-b057-c48490294ddd",
            "created": "2022-10-19T10:30:48.055519Z",
            "updated": "2023-05-17T07:15:51.700130Z",
            "details": "http://localhost:8000/api/v1/findingtemplates/e6961177-0582-4dd2-b057-c48490294ddd",
            "lock_info": None,
            "usage_count": 1,
            "source": "imported",
            "tags": ["web"],
            "language": "en-US",
            "status": "in-progress",
            "data": {
                "title": "SQL Injection (SQLi)",
            },
        }

        base_importer = BaseImporter.BaseImporter(reptor=self.reptor)
        base_importer.convert_old_tools_references = convert_old_tools_references
        base_importer.reptor._api = Api()
        base_importer.mapping = {
            "old_tools_title": "title",
            "old_tools_description": "description",
            "old_tools_cvss_vector": "cvss",
            "old_tools_custom_field": "custom_field",
            "old_tools_empty_field": "empty_field",
            "old_tools_missing_field": "missing_field",
            "old_tools_references": "references",
            "recommendation_part_1": "recommendation",
            "recommendation_part_2": "recommendation",
            "recommendation_part_3": "recommendation",
        }

        finding_data = {
            "language": "en-US",
            "status": "in-progress",
            "data": {
                "old_tools_title": "my title",
                "old_tools_description": "my description",
                "old_tools_cvss_vector": "CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:H",
                "old_tools_custom_field": "custom info",
                "old_tools_empty_field": "",
                "old_tools_references": "reference1\nreference2\r\nreference3",
                "recommendation_part_1": "do this!",
                "recommendation_part_2": "do that!",
                "recommendation_part_3": "do nothing!",
            },
        }
        finding = base_importer._create_finding_item(finding_data)
        assert isinstance(finding, FindingTemplate)
        assert finding.translations[0].language == "en-US"
        assert finding.translations[0].status == "in-progress"

        assert finding.translations[0].data.title == "my title"
        assert finding.translations[0].data.description == "my description"
        assert (
            finding.translations[0].data.cvss
            == "CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:H"
        )
        assert finding.translations[0].data.custom_field == "custom info"
        assert finding.translations[0].data.empty_field == ""
        with pytest.raises(AttributeError):
            finding.translations[0].data.missing_field
        assert finding.translations[0].data.references == [
            "reference1",
            "reference2",
            "reference3",
        ]
        assert (
            finding.translations[0].data.recommendation
            == "do this!\ndo that!\ndo nothing!"
        )

        base_importer._upload_finding_template(finding)
