from reptor.lib.modules.ToolBase import ToolBase


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
        self.oG = kwargs.get("oG")
        self.oX = kwargs.get("oX")
        self.notename = "nmap scan"
        self.note_icon = "👁️‍🗨️"

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        nmap_output_parser = parser.add_mutually_exclusive_group()
        nmap_output_parser.add_argument(
            "-oG", help="nmap Grepable output format", action="store_true"
        )
        nmap_output_parser.add_argument(
            "-oX", help="nmap XML output format", action="store_true"
        )

    def _parse_grepable(self, raw_input):
        parsed_input = list()
        for line in raw_input.splitlines():
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
                    parsed_input.append(
                        {
                            "ip": ip,
                            "port": port,
                            "protocol": protocol,
                            "service": service.replace("|", "/"),
                            "version": version.replace("|", "/"),
                        }
                    )
        return parsed_input

    def parse(self):
        super().parse()
        if self.oX:
            # TODO parse XML
            raise TypeError("nmap -oX format (XML) not yet implemented")
        else:
            # Default: -oG
            self.parsed_input = self._parse_grepable(self.raw_input)

    def format(self):
        super().format()
        # TODO put md table creation to utils function
        lines = list()
        headings = ["Host", "Port", "Service", "Version"]
        lines.append(f"| {' | '.join(headings)} |")
        lines.append("| ------- " * len(headings) + "|")

        for port in self.parsed_input:
            lines.append(
                f"| {port['ip']} | {port['port']}/{port['protocol']} | {port['service'] or 'n/a'} | {port['version'] or 'n/a'} |"
            )

        lines.extend(["", ": nmap scan results"])
        self.formatted_input = "\n".join(lines)


loader = Nmap
