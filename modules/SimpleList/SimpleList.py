from classes.ToolBase import ToolBase


class SimpleList(ToolBase):
    """
    format list output

    Sample commands:

        # Format
        cat subdomains.txt | reptor simplelist
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = 'simplelist'
        self.note_icon = '👁️‍🗨️'

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        nmap_output_parser = parser.add_mutually_exclusive_group()
        nmap_output_parser.add_argument("-num",
                                        help="Create as numeric list",
                                        action="store_true")
        nmap_output_parser.add_argument("-header",
                                        help="Set a header",
                                        action="store_true")

    def parse(self):
        super().parse()

    def format(self):
        super().format()


loader = SimpleList
