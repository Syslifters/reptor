from reptor.lib.plugins.ToolBase import ToolBase
from reptor.plugins.tools.Nmap.models import Service


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
        self.notename = kwargs.get("notename", "Nmap Scan")
        self.note_icon = "👁️‍🗨️"
        if self.input_format == "raw":
            self.input_format = "xml"

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        input_format_group = cls.get_input_format_group(parser)
        input_format_group.add_argument(
            "-oX",
            help="nmap XML output format, same as --xml (recommended)",
            action="store_const",
            dest="format",
            const="xml",
        )
        input_format_group.add_argument(
            "-oG",
            "--grepable",
            help="nmap Grepable output format",
            action="store_const",
            dest="format",
            const="grepable",
        )

        parser.add_argument(
            "-multi-notes",
            "--multi-notes",
            help="Uploads multiple notes (one per IP) instead of one note with all IPs",
            action="store_true",
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
                            "port": port,
                            "protocol": protocol,
                            "service": service.replace("|", "/"),
                            "version": version.replace("|", "/"),
                        }
                    )
                    self.parsed_input.append(s)

    def parse_xml(self):
        super().parse_xml()
        nmap_data = self.parsed_input
        self.parsed_input = list()
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
                            "hostname": (host.get("hostnames") or {})
                            .get("hostname", {})
                            .get("@name"),
                            "port": port.get("@portid"),
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

    def preprocess_for_template(self):
        data = dict()
        if not self.multi_notes:
            data["data"] = self.parsed_input
            data["show_hostname"] = any([s.hostname for s in self.parsed_input])
        else:
            # Group data per IP
            for d in self.parsed_input:
                # Key of the dict (d.ip) will be title of the note
                data.setdefault(d.ip, list()).append(d)
            # Show hostname or not
            for ip, port_data in data.items():
                data[ip] = {
                    "data": port_data,
                    "show_hostname": any([s.hostname for s in port_data]),
                }

        return data


loader = Nmap
