from reptor.lib.plugins.ToolBase import ToolBase
from reptor.models.Note import NoteTemplate


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
        self.note_icon = "👁️‍🗨️"
        self.notetitle = kwargs.get("notetitle") or "Nmap"
        if self.input_format == "raw":
            self.input_format = "xml"

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
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
                    self.parsed_input.append(
                        {
                            "ip": ip,
                            "port": port,
                            "hostname": "",  # No hostname in greppable output
                            "protocol": protocol,
                            "service": service.replace("|", "/"),
                            "version": version.replace("|", "/"),
                        }
                    )

    def parse_xml(self):
        super().parse_xml()
        nmap_data = self.parsed_input
        self.parsed_input = list()
        hosts = nmap_data.get("nmaprun", {}).get("host", [])
        if not isinstance(hosts, list):
            hosts = [hosts]
        for host in hosts:
            netif_addrs = host.get("address", [])
            if not isinstance(netif_addrs, list):
                netif_addrs = [netif_addrs]
            # predefine value if error occurred
            ip = "ERROR"
            for if_addr in netif_addrs:
                # skip mac address, only ipv4/ipv6 address should be included
                if if_addr["@addrtype"].startswith("ip"):
                    # get ip address from scan result
                    ip = if_addr.get("@addr")
            ports = host.get("ports", {}).get("port", [])
            if not isinstance(ports, list):
                ports = [ports]
            for port in ports:
                if port.get("state", {}).get("@state") == "open":
                    self.parsed_input.append(
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

    def parse(self):
        super().parse()
        if self.input_format == "grepable":
            self.parse_grepable()

    def preprocess_for_template(self) -> dict:
        show_hostname = any([s.get("hostname") for s in self.parsed_input])
        return {"data": self.parsed_input, "show_hostname": show_hostname}

    def create_notes(self):
        data = dict()
        # Group by IP
        for ports in self.parsed_input:
            if ports["ip"] not in data:
                data[ports["ip"]] = list()
            data[ports["ip"]].append(ports)

        # Create note structure
        ## Main note with table of all IPs
        main_note = NoteTemplate()
        main_note.title = self.notetitle
        main_note.icon_emoji = self.note_icon
        main_note.template = self.template
        main_note.template_data = self.preprocess_for_template()
        ## Subnotes per IP
        for ip, ports in data.items():
            ip_note = NoteTemplate()
            ip_note.title = ip
            ip_note.checked = False
            ip_note.template = self.template
            ip_note.template_data = {"data": ports}
            ip_note.template_data["show_hostname"] = any(
                [p.get("hostname") for p in ports]
            )
            main_note.children.append(ip_note)
        return main_note


loader = Nmap
