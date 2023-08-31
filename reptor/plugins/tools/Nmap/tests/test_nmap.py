import os
from pathlib import Path

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin

from ..models import Service
from ..Nmap import Nmap


class TestNmap(TestCaseToolPlugin):
    templates_path = os.path.normpath(Path(os.path.dirname(__file__)) / "../templates")

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        Nmap.setup_class(
            Path(os.path.dirname(self.templates_path)), skip_user_plugins=True
        )
        self.nmap = Nmap(reptor=self.reptor)

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
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        assert parsed_input_dict == result_dict

    def test_xml_parse_multi_target(self):
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
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        for entry in entries:
            assert entry in parsed_input_dict

    def test_multi_notes(self):
        """
        result = {
            "142.250.180.228": {
                "data": [
                    {
                        "hostname": "www.google.com",
                        "ip": "142.250.180.228",
                        "port": "80",
                        "protocol": "tcp",
                        "service": "http",
                        "version": "gws",
                    },
                    {
                        "hostname": "www.google.com",
                        "ip": "142.250.180.228",
                        "port": "443",
                        "protocol": "tcp",
                        "service": "https",
                        "version": "gws",
                    },
                ],
                "show_hostname": True,
            },
            "34.249.200.254": {
                "data": [
                    {
                        "hostname": "www.syslifters.com",
                        "ip": "34.249.200.254",
                        "port": "80",
                        "protocol": "tcp",
                        "service": "http",
                        "version": None,
                    },
                    {
                        "hostname": "www.syslifters.com",
                        "ip": "34.249.200.254",
                        "port": "443",
                        "protocol": "tcp",
                        "service": "https",
                        "version": None,
                    },
                ],
                "show_hostname": True,
            },
        }
        """

        self._load_xml_data("nmap_multi_target.xml")
        self.nmap.multi_notes = True
        self.nmap.parse()
        data = self.nmap.preprocess_for_template()
        assert "34.249.200.254" in data
        assert "142.250.180.228" in data
        assert isinstance(data["34.249.200.254"], dict)
        assert isinstance(data["142.250.180.228"], dict)
        assert "data" in data["34.249.200.254"]
        assert "data" in data["142.250.180.228"]
        assert "show_hostname" in data["34.249.200.254"]
        assert "show_hostname" in data["142.250.180.228"]
        assert len(data["34.249.200.254"]["data"]) == 2
        assert len(data["142.250.180.228"]["data"]) == 2

        assert data["142.250.180.228"]["data"][0].ip == "142.250.180.228"
        assert data["34.249.200.254"]["data"][0].ip == "34.249.200.254"

        self.nmap.format()
        assert isinstance(self.nmap.formatted_input, dict)
        assert "142.250.180.228" in self.nmap.formatted_input
        assert "34.249.200.254" in self.nmap.formatted_input
        assert (
            self.nmap.formatted_input["34.249.200.254"]
            == "| Hostname | IP | Port | Service | Version |\n| ------- | ------- | ------- | ------- | ------- |\n| www.syslifters.com | 34.249.200.254 | 80/tcp | http | n/a |\n| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
        )
        assert (
            self.nmap.formatted_input["142.250.180.228"]
            == "| Hostname | IP | Port | Service | Version |\n| ------- | ------- | ------- | ------- | ------- |\n| www.google.com | 142.250.180.228 | 80/tcp | http | gws |\n| www.google.com | 142.250.180.228 | 443/tcp | https | gws |"
        )

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
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        for entry in entries:
            assert entry in parsed_input_dict

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
        parsed_input_dict = [p.__dict__ for p in self.nmap.parsed_input]
        for entry in entries:
            assert entry in parsed_input_dict

    def test_process_parsed_input(self):
        # test without hostname
        self.nmap.parsed_input = list()
        for d in [
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
        ]:
            s = Service()
            s.parse(d)
            self.nmap.parsed_input.append(s)

        data = self.nmap.preprocess_for_template()
        assert data == {"data": self.nmap.parsed_input, "show_hostname": False}

        # test with hostname
        self.nmap.parsed_input = list()
        for d in [
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
        ]:
            s = Service()
            s.parse(d)
            self.nmap.parsed_input.append(s)

        data = self.nmap.preprocess_for_template()
        assert data == {"data": self.nmap.parsed_input, "show_hostname": True}

    def test_format_nmap(self):
        result = """| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | nginx (reverse proxy) |
| 127.0.0.1 | 443/tcp | ssl/http | nginx (reverse proxy) |
| 127.0.0.1 | 8080/tcp | n/a | n/a |"""
        self._load_grepable_data()
        self.nmap.format()
        assert self.nmap.formatted_input == result

        result = """| Hostname | IP | Port | Service | Version |
| ------- | ------- | ------- | ------- | ------- |
| www.syslifters.com | 63.35.51.142 | 80/tcp | http | n/a |"""
        self.nmap.parsed_input = None
        self._load_xml_data("nmap_single_target_single_port.xml")
        self.nmap.format()
        assert self.nmap.formatted_input == result
