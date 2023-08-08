import os
import unittest

import django
from django.conf import settings

from reptor.lib.conf import settings as reptor_settings
from reptor.lib.reptor import Reptor

from ..models import Service
from ..Nmap import Nmap

templates_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '../templates'))
reptor_settings.TEMPLATES[0]['DIRS'].append(templates_path)
settings.configure(reptor_settings, DEBUG=True)
django.setup()


class NmapTests(unittest.TestCase):
    def setUp(self) -> None:
        reptor = Reptor()
        Nmap.set_template_vars(os.path.dirname(templates_path))
        self.nmap = Nmap(reptor=reptor)

        return super().setUp()

    def _load_grepable_data(self):
        self.nmap.input_format = 'grepable'
        filepath = os.path.join(
            os.path.dirname(__file__), './data/grepable.txt')
        with open(filepath, 'r') as f:
            self.nmap.raw_input = f.read()

    def _load_xml_data(self, xml_file):
        self.nmap.input_format = 'xml'
        filepath = os.path.join(
            os.path.dirname(__file__), f'./data/{xml_file}')
        with open(filepath, 'r') as f:
            self.nmap.raw_input = f.read()

    def test_grepable_parse(self):
        result_dict = [{'ip': '127.0.0.1', 'hostname': '', 'port': 80, 'protocol': 'tcp',
                        'service': 'http', 'version': 'nginx (reverse proxy)'},
                       {'ip': '127.0.0.1', 'hostname': '', 'port': 443, 'protocol': 'tcp',
                        'service': 'ssl/http', 'version': 'nginx (reverse proxy)'},
                       {'ip': '127.0.0.1', 'hostname': '', 'port': 8080,
                           'protocol': 'tcp', 'service': '', 'version': ''}
                       ]
        self._load_grepable_data()
        self.nmap.parse()
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        self.assertEqual(parsed_input_dict, result_dict)

    def test_xml_parse_multi_target(self):
        entries = [{
            'ip': '142.250.180.228',
            'hostname': 'www.google.com',
            'port': 80,
            'protocol': 'tcp',
            'service': 'http',
            'version': 'gws'
        }, {
            'ip': '142.250.180.228',
            'hostname': 'www.google.com',
            'port': 443,
            'protocol': 'tcp',
            'service': 'https',
            'version': 'gws'
        }, {
            'ip': '34.249.200.254',
            'hostname': 'www.syslifters.com',
            'port': 80,
            'protocol': 'tcp',
            'service': 'http',
            'version': None
        }, {
            'ip': '34.249.200.254',
            'hostname': 'www.syslifters.com',
            'port': 443,
            'protocol': 'tcp',
            'service': 'https',
            'version': None
        }]
        self._load_xml_data('nmap_multi_target.xml')
        self.nmap.parse()
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        for entry in entries:
            self.assertIn(entry, parsed_input_dict)
            

    def test_xml_parse_single_target(self):
        entries = [{
            'ip': '63.35.51.142',
            'hostname': 'www.syslifters.com',
            'port': 80,
            'protocol': 'tcp',
            'service': 'http',
            'version': None
        }]
        self._load_xml_data('nmap_single_target_single_port.xml')
        self.nmap.parse()
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        for entry in entries:
            self.assertIn(entry, parsed_input_dict)

    def test_xml_parse_without_hostname(self):
        entries = [{
            'ip': '142.251.208.164',
            'hostname': None,
            'port': 80,
            'protocol': 'tcp',
            'service': 'http',
            'version': None
        }, {
            'ip': '142.251.208.164',
            'hostname': None,
            'port': 443,
            'protocol': 'tcp',
            'service': 'https',
            'version': None
        }]
        self._load_xml_data('nmap_without_hostname.xml')
        self.nmap.parse()
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        for entry in entries:
            self.assertIn(entry, parsed_input_dict)

    def test_process_parsed_input(self):
        # test without hostname
        self.nmap.parsed_input = list()
        for d in [{'ip': '127.0.0.1', 'hostname': '', 'port': 80, 'protocol': 'tcp',
                        'service': 'http', 'version': 'nginx (reverse proxy)'},
                  {'ip': '127.0.0.1', 'hostname': '', 'port': 443, 'protocol': 'tcp',
                        'service': 'ssl/http', 'version': 'nginx (reverse proxy)'}]:
            s = Service()
            s.parse(d)
            self.nmap.parsed_input.append(s)

        data = self.nmap.process_parsed_input_for_template()
        self.assertEqual(data, {'parsed_input': self.nmap.parsed_input, 'show_hostname': False})
        
        # test with hostname
        self.nmap.parsed_input = list()
        for d in [{'ip': '127.0.0.1', 'hostname': '', 'port': 80, 'protocol': 'tcp',
                        'service': 'http', 'version': 'nginx (reverse proxy)'},
                  {'ip': '127.0.0.1', 'hostname': 'localhost', 'port': 443, 'protocol': 'tcp',
                        'service': 'ssl/http', 'version': 'nginx (reverse proxy)'}]:
            s = Service()
            s.parse(d)
            self.nmap.parsed_input.append(s)

        data = self.nmap.process_parsed_input_for_template()
        self.assertEqual(data, {'parsed_input': self.nmap.parsed_input, 'show_hostname': True})
        

    def test_format_nmap(self):
        result = """| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | nginx (reverse proxy) |
| 127.0.0.1 | 443/tcp | ssl/http | nginx (reverse proxy) |
| 127.0.0.1 | 8080/tcp | n/a | n/a |"""
        self._load_grepable_data()
        self.nmap.format()
        #print(self.nmap.formatted_input)
        self.assertEqual(self.nmap.formatted_input, result)


        result = """| Hostname | Host | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
| www.syslifters.com | 63.35.51.142 | 80/tcp | http | n/a |"""
        self.nmap.parsed_input = None
        self._load_xml_data('nmap_single_target_single_port.xml')
        self.nmap.format()
        self.assertEqual(self.nmap.formatted_input, result)