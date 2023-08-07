import os
import unittest

import django
from django.conf import settings

from reptor.lib.conf import settings as reptor_settings
from reptor.lib.reptor import Reptor

from ..Sslyze import Sslyze

templates_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../templates'))
reptor_settings.TEMPLATES[0]['DIRS'].append(templates_path)
settings.configure(reptor_settings, DEBUG=True)
django.setup()


class SslyzeTests(unittest.TestCase):
    def setUp(self) -> None:
        reptor = Reptor()
        Sslyze.set_template_vars(os.path.dirname(templates_path))
        self.sslyze = Sslyze(reptor=reptor)

        return super().setUp()

    def _load_json_data(self):
        self.sslyze.input_format = 'json'
        filepath = os.path.join(
            os.path.dirname(__file__), './data/sslyze.json')
        with open(filepath, 'r') as f:
            self.sslyze.raw_input = f.read()

    def test_parse(self):
        result_dict = []
        self._load_json_data()
        self.sslyze.parse()
        parsed_input_dict = [p.__dict__ for p in self.sslyze.parsed_input]
        self.assertEqual(parsed_input_dict, result_dict)

    def test_format_nmap(self):
        #result = """| Host | Port | Service | Version |"""
        #self._load_json_data()
        #self.sslyze.format()
        #self.assertEqual(self.sslyze.formatted_input.strip('\n'), result)
        pass