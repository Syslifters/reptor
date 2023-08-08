import xmltodict

from reptor.lib.plugins.ToolBase import ToolBase
from reptor.plugins.core.Nmap.models import Service


class Nmap(ToolBase):
    """
    Author: Syslifters
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: network,scanning,infrastructure

    Short Help:
    Formats nmap output

    Description:
    target=127.0.0.1
    sudo nmap -Pn -n -sV -oG - -p 1-65535 $target

    sudo -v  # Elevate privileges for non-interactive
    sudo -n nmap -Pn -n -sV -oG - -p 80,440 $target | tee nmap_result.txt | reptor nmap

    # Format and upload
    cat nmap_result.txt | reptor nmap -c upload
    """
    meta = {
        "name": "Nmap",
        "summary": "format nmap output",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = "nmap scan"
        self.note_icon = "👁️‍🗨️"
        if self.input_format == "raw":
            self.input_format = "grepable"

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        # Find input_format_group
        for group in parser._mutually_exclusive_groups:
            if group.title == "input_format_group":
                break
        else:
            return

        group.add_argument(
            "-oX",
            help="nmap XML output format, same as --xml",
            action="store_const",
            dest="format",
            const="xml",
        )
        group.add_argument(
            "-oG",
            "--grepable",
            help="nmap Grepable output format",
            action="store_const",
            dest="format",
            const="grepable",
        )

    def parse_grepable(self):
        self.parsed_input = list()
        for line in self.raw_input.splitlines():
            if line.startswith("#") or "Ports:" not in line:
                continue
            ip, ports = line.split("Ports:")
            ip = ip.split(" ")[1]
            
            ports = ports.split(",")
            for port in ports:
                port, status, protocol, _, service, _, version, _ = port.strip().split(
                    "/"
                )
                if status == "open":
                    s = Service()
                    s.parse(
                        {
                            "ip": ip,
                            "port": int(port),
                            "protocol": protocol,
                            "service": service.replace("|", "/"),
                            "version": version.replace("|", "/"),
                        }
                    )
                    self.parsed_input.append(s)

    def parse_xml(self):
        self.parsed_input = list()
        nmap_data = xmltodict.parse(self.raw_input)
        hosts = nmap_data.get("nmaprun", {}).get("host", [])
        if not isinstance(hosts, list):
                hosts = [hosts]
        for host in hosts:
            ip = host.get("address", {}).get("@addr")
            ports = host.get("ports", {}).get("port", [])
            if not isinstance(ports, list):
                ports = [ports]
            for port in ports:
                if port.get("state", {}).get("@state") == "open":
                    s = Service()
                    s.parse(
                        {
                            "ip": ip,
                            "hostname": (host.get("hostnames") or {}).get("hostname", {}).get("@name"),
                            "port": int(port.get("@portid")),
                            "protocol": port.get("@protocol"),
                            "service": port.get("service", {}).get("@name"),
                            "version": port.get("service", {}).get("@product"),
                        }
                    )
                    self.parsed_input.append(s)

    def parse(self):
        super().parse()
        if self.input_format == "grepable":
            self.parse_grepable()

    def process_parsed_input_for_template(self, template=None):
        data = dict()
        data['parsed_input'] = self.parsed_input
        data['show_hostname'] = any([s.hostname for s in self.parsed_input])
        return data

loader = Nmap
