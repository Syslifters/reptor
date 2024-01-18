from unittest.mock import Mock

import django
from django.conf import settings
from django.template import engines

from reptor.api.APIClient import APIClient
from reptor.api.manager import APIManager
from reptor.lib.conf import Config
from reptor.lib.conf import settings as reptor_settings
from reptor.lib.reptor import Reptor

settings.configure(reptor_settings, DEBUG=True)
django.setup()


class TestCaseToolPlugin:
    @classmethod
    def setup_class(cls):
        cls.reptor = Reptor()
        cls.patch_apis()

        settings.TEMPLATES[0]["DIRS"] = [cls.templates_path]
        try:
            engines._engines["django"].engine.dirs = [cls.templates_path]
        except KeyError:
            pass

    @classmethod
    def teardown_class(cls):
        settings.TEMPLATES[0]["DIRS"] = []
        try:
            engines._engines["django"].engine.dirs = []
        except KeyError:
            pass

    @classmethod
    def patch_apis(cls):
        cls.reptor._api = APIManager(reptor=cls.reptor)
        cls.reptor._config = Config()
        cls.reptor._config._raw_config = {
            "project_id": "db837c68-ff58-4f63-9161-d2310d71999b",
            "server": "https://demo.sysre.pt",
            "token": "sysreptor_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
        }
        APIClient.get = APIClient.post = APIClient.put = APIClient.patch = Mock(
            side_effect=RuntimeError(
                "APIClient cannot be used in tests. Patch methods as needed."
            )
        )
