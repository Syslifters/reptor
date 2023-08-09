import django
from django.conf import settings
from django.template import engines

from reptor.lib.conf import settings as reptor_settings
from reptor.lib.reptor import Reptor

settings.configure(reptor_settings, DEBUG=True)
django.setup()


class TestCaseToolPlugin:
    @classmethod
    def setup_class(cls):
        cls.reptor = Reptor()

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
