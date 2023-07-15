import typing

from reptor.lib.interfaces.reptor import ReptorProtocol
from reptor.api.models import FindingTemplate, FindingData
from reptor.api.TemplatesAPI import TemplatesAPI


class BaseImporter:
    reptor: ReptorProtocol
    mapping: typing.Dict

    def __init__(self, reptor: ReptorProtocol, **kwargs) -> None:
        self.reptor = reptor

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        ...

    def next_findings_batch(self):
        """Implement this to yield the next findings to process"""
        return None

    def _create_finding_item(self, raw_data: typing.Dict) -> FindingTemplate:
        remapped_data = dict()
        for key, value in self.mapping.items():
            converted_data = raw_data[key]
            # check if we have a convert_method and call it
            # update the value
            convert_method_name = f"convert_{key}"
            if hasattr(self, convert_method_name):
                if callable(getattr(self, convert_method_name)):
                    converter_method = getattr(self, convert_method_name)
                    self.reptor.logger.debug(f"Calling: {convert_method_name}")
                    converted_data = converter_method(raw_data[key])

            remapped_data[value] = converted_data

        new_finding = FindingTemplate(remapped_data)
        new_finding.data = FindingData(remapped_data)
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
        if not self.mapping:
            self.reptor.logger.fail_with_exit("You need to provide a mapping.")

        for external_finding in self.next_findings_batch():
            new_finding = self._create_finding_item(external_finding)
            if not new_finding:
                continue
            self.reptor.logger.display(f"Uploading {new_finding.data.title}")
            self.reptor.logger.debug(new_finding)
            self._upload_finding_templates(new_finding)
