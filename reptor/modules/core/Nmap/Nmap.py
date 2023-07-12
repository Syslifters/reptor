
from reptor.lib.modules.ToolBase import ToolBase
from reptor.modules.core.Nmap.models import Service


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = "nmap scan"
        self.note_icon = "👁️‍🗨️"
        if self.input_format == 'raw':
            self.input_format = 'grepable'

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        # Find input_format_group
        for group in parser._mutually_exclusive_groups:
            if group.title == 'input_format_group':
                break
        else:
            return

        group.add_argument(
            "-oX",
            help="nmap XML output format, same as --xml",
            action="store_const",
            dest="format",
            const="xml"
        )
        group.add_argument(
            "-oG",
            "--grepable",
            help="nmap Grepable output format",
            action="store_const",
            dest="format",
            const="grepable"
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
                    s.parse({
                        "ip": ip,
                        "port": int(port),
                        "protocol": protocol,
                        "service": service.replace("|", "/"),
                        "version": version.replace("|", "/"),
                    })
                    self.parsed_input.append(s)

    def parse_xml(self):
        # TODO parse XML
        raise TypeError("nmap -oX format (XML) not yet implemented")

    def parse(self):
        super().parse()
        if self.input_format == "grepable":
            self.parse_grepable()


loader = Nmap
