import os
from pathlib import Path

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin

from ..Nmap import Nmap


class TestNmap(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Nmap.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.nmap = Nmap(reptor=self.reptor, template=Nmap.template)

    def _load_grepable_data(self):
        self.nmap.input_format = "grepable"
        filepath = os.path.join(os.path.dirname(__file__), "./data/grepable.txt")
        with open(filepath, "r") as f:
            self.nmap.raw_input = f.read()

    def _load_xml_data(self, xml_file):
        self.nmap.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{xml_file}")
        with open(filepath, "r") as f:
            self.nmap.raw_input = f.read()

    def test_grepable_parse(self):
        result_dict = [
            {
                "ip": "127.0.0.1",
                "hostname": "",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": "nginx (reverse proxy)",
            },
            {
                "ip": "127.0.0.1",
                "hostname": "",
                "port": "443",
                "protocol": "tcp",
                "service": "ssl/http",
                "version": "nginx (reverse proxy)",
            },
            {
                "ip": "127.0.0.1",
                "hostname": "",
                "port": "8080",
                "protocol": "tcp",
                "service": "",
                "version": "",
            },
        ]
        self._load_grepable_data()
        self.nmap.parse()
        assert self.nmap.parsed_input == result_dict

    def test_xml_parse_with_mac(self):
        entries = [
            {
                "ip": "142.250.180.228",
                "hostname": "www.google.com",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": "gws",
            },
            {
                "ip": "142.250.180.228",
                "hostname": "www.google.com",
                "port": "443",
                "protocol": "tcp",
                "service": "https",
                "version": "gws",
            },
            {
                "ip": "34.249.200.254",
                "hostname": "www.syslifters.com",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": None,
            },
            {
                "ip": "34.249.200.254",
                "hostname": "www.syslifters.com",
                "port": "443",
                "protocol": "tcp",
                "service": "https",
                "version": None,
            },
        ]
        self._load_xml_data("nmap_multi_target.xml")
        self.nmap.parse()
        for entry in entries:
            assert entry in self.nmap.parsed_input

    def test_xml_parse_multi_target(self):
        entries = [
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "22",
                "protocol": "tcp",
                "service": "ssh",
                "version": "OpenSSH",
            },
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "25",
                "protocol": "tcp",
                "service": "smtp-proxy",
                "version": "Python SMTP Proxy",
            },
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": "Golang net/http server",
            },
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "443",
                "protocol": "tcp",
                "service": "http",
                "version": "Golang net/http server",
            },
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "2222",
                "protocol": "tcp",
                "service": "ssh",
                "version": "OpenSSH",
            },
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "8080",
                "protocol": "tcp",
                "service": "http",
                "version": "Golang net/http server",
            },
            {
                "ip": "192.168.1.69",
                "hostname": None,
                "port": "9999",
                "protocol": "tcp",
                "service": "abyss",
                "version": None,
            },
        ]
        self._load_xml_data("nmap_with_mac.xml")
        self.nmap.parse()
        for entry in entries:
            assert entry in self.nmap.parsed_input

    def test_xml_parse_single_target(self):
        entries = [
            {
                "ip": "63.35.51.142",
                "hostname": "www.syslifters.com",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": None,
            }
        ]
        self._load_xml_data("nmap_single_target_single_port.xml")
        self.nmap.parse()
        for entry in entries:
            assert entry in self.nmap.parsed_input

    def test_xml_parse_without_hostname(self):
        entries = [
            {
                "ip": "142.251.208.164",
                "hostname": None,
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": None,
            },
            {
                "ip": "142.251.208.164",
                "hostname": None,
                "port": "443",
                "protocol": "tcp",
                "service": "https",
                "version": None,
            },
        ]
        self._load_xml_data("nmap_without_hostname.xml")
        self.nmap.parse()
        for entry in entries:
            assert entry in self.nmap.parsed_input

    def test_process_parsed_input(self):
        # test without hostname
        self.nmap.parsed_input = [
            {
                "ip": "127.0.0.1",
                "hostname": "",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": "nginx (reverse proxy)",
            },
            {
                "ip": "127.0.0.1",
                "hostname": "",
                "port": "443",
                "protocol": "tcp",
                "service": "ssl/http",
                "version": "nginx (reverse proxy)",
            },
        ]

        data = self.nmap.preprocess_for_template()
        assert data == {"data": self.nmap.parsed_input, "show_hostname": False}

        # test with hostname
        self.nmap.parsed_input = [
            {
                "ip": "127.0.0.1",
                "hostname": "",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
                "version": "nginx (reverse proxy)",
            },
            {
                "ip": "127.0.0.1",
                "hostname": "localhost",
                "port": "443",
                "protocol": "tcp",
                "service": "ssl/http",
                "version": "nginx (reverse proxy)",
            },
        ]

        data = self.nmap.preprocess_for_template()
        assert data == {"data": self.nmap.parsed_input, "show_hostname": True}

    def test_format_nmap(self):
        result = """# Nmap

| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | nginx (reverse proxy) |
| 127.0.0.1 | 443/tcp | ssl/http | nginx (reverse proxy) |
| 127.0.0.1 | 8080/tcp | n/a | n/a |

## 127.0.0.1

| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | nginx (reverse proxy) |
| 127.0.0.1 | 443/tcp | ssl/http | nginx (reverse proxy) |
| 127.0.0.1 | 8080/tcp | n/a | n/a |
"""
        self._load_grepable_data()
        self.nmap.format()
        assert isinstance(self.nmap.formatted_input, str)
        assert self.nmap.formatted_input.strip() == result.strip()

        result = """# Nmap

| Hostname | IP | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
| www.syslifters.com | 63.35.51.142 | 80/tcp | http | n/a |

## 63.35.51.142

| Hostname | IP | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
| www.syslifters.com | 63.35.51.142 | 80/tcp | http | n/a |"""
        self.nmap.parsed_input = None
        self._load_xml_data("nmap_single_target_single_port.xml")
        self.nmap.format()
        assert isinstance(self.nmap.formatted_input, str)
        assert self.nmap.formatted_input.strip() == result.strip()
