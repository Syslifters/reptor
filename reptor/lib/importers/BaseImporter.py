import typing

from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.api.models import FindingTemplate, FindingData
from reptor.api.TemplatesAPI import TemplatesAPI


class BaseImporter:
    reptor: ReptorProtocol

    def __init__(self, reptor: ReptorProtocol, **kwargs) -> None:
        self.reptor = reptor

    @classmethod
    def add_arguments(cls, parser):
        ...

    def convert_to_sysreptor_template(self) -> typing.Dict:
        """Implement this and call self.import_finding(mapped_data)"""
        return {}

    def _create_finding_item(self, raw_data: typing.Dict) -> FindingTemplate:
        new_finding = FindingTemplate(raw_data)
        new_finding.data = FindingData(raw_data)
        return new_finding

    def _upload_finding_templates(self, new_finding: FindingTemplate):
        updated_template = TemplatesAPI(self.reptor).upload_new_template(new_finding)
        if updated_template:
            self.reptor.logger.display(f"Uploaded {updated_template.id}")
        else:
            self.reptor.logger.fail("Do you want to abort? [Y/n]")
            abort_answer = input()[:1].lower()
            if abort_answer != "n":
                self.reptor.logger.fail_with_exit("Aborting...")

    def run(self):
        normalized_data = self.convert_to_sysreptor_template()
        new_finding = self._create_finding_item(normalized_data)
        self._upload_finding_templates(new_finding)
