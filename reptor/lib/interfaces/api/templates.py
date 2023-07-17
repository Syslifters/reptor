import typing
from abc import abstractmethod

from .base import BaseApiProtocol


class ApiTemplatesProtocol(BaseApiProtocol):
    project_id: str
