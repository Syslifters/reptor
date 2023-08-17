import typing
from abc import abstractmethod

from reptor.models.FindingTemplate import FindingTemplate

from .base import BaseApiProtocol


class ApiTemplatesProtocol(BaseApiProtocol):
    project_id: str

    @abstractmethod
    def upload_new_template(
        self, template: FindingTemplate
    ) -> typing.Optional[FindingTemplate]:
        ...
