from abc import abstractmethod

from .base import BaseApiProtocol
from .models import ProjectDesignProtocol


class ApiProjectDesignsProtocol(BaseApiProtocol):
    project_design_id: str

    @abstractmethod
    def project_design(self) -> ProjectDesignProtocol:
        ...
