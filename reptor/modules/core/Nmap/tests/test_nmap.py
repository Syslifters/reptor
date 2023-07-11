import os
import unittest

import django
from django.conf import settings

from reptor.lib.conf import settings as reptor_settings
from reptor.lib.reptor import Reptor

from ..Nmap import Nmap

templates_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../templates'))
reptor_settings.TEMPLATES[0]['DIRS'].append(templates_path)
settings.configure(reptor_settings, DEBUG=True)
django.setup()


class NmapTests(unittest.TestCase):
    def setUp(self) -> None:
        reptor = Reptor()
        reptor._load_config()
        self.nmap = Nmap(reptor=reptor)

        return super().setUp()

    def _load_grepable_data(self):
        filepath = os.path.join(
            os.path.dirname(__file__), './data/grepable.txt')
        with open(filepath, 'r') as f:
            self.nmap.raw_input = f.read()

    def test_grepable_parse(self):
        result_dict = [{'ip': '127.0.0.1', 'port': 80, 'protocol': 'tcp',
                        'service': 'http', 'version': 'nginx (reverse proxy)'},
                       {'ip': '127.0.0.1', 'port': 443, 'protocol': 'tcp',
                        'service': 'ssl/http', 'version': 'nginx (reverse proxy)'},
                       {'ip': '127.0.0.1', 'port': 8080,
                           'protocol': 'tcp', 'service': '', 'version': ''}
                       ]
        self._load_grepable_data()
        self.nmap.parse()
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        self.assertEqual(parsed_input_dict, result_dict)

    def test_format_nmap(self):
        result = """| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | nginx (reverse proxy) |
| 127.0.0.1 | 443/tcp | ssl/http | nginx (reverse proxy) |
| 127.0.0.1 | 8080/tcp | n/a | n/a |"""
        self._load_grepable_data()
        self.nmap.format()
        self.assertEqual(self.nmap.formatted_input.strip('\n'), result)
