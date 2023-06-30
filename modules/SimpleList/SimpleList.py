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
        self.note_icon = '📃'
        self.arg_num = kwargs.get('num')
        self.arg_header = kwargs.get('header')

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        simplelist_parser = parser.add_argument_group()
        simplelist_parser.add_argument("--num",
                                        help="Create as numeric list",
                                        action="store_true")

        simplelist_parser.add_argument("--header",
                                        help="Set a header",
                                        action="store",)

    def parse(self):
        super().parse()
        parsed_input = list()
        if self.arg_header:
            parsed_input.append(f"# {self.arg_header}")

        for i, line in enumerate(self.raw_input.splitlines()):
            i += 1
            if self.arg_num:
                parsed_input.append(f"{i} {line}")
            else:
                parsed_input.append(f"- {line}")

        self.parsed_input = parsed_input

    def format(self):
        super().format()
        self.formatted_input = "\n".join(self.parsed_input)


loader = SimpleList
