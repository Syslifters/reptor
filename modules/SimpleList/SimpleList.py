from classes.ToolBase import ToolBase


class SimpleList(ToolBase):
    """
    format list output

    Sample commands:

        # Format
        cat subdomains.txt | reptor simplelist -c format

        # Upload with level 4 heading and numeric
        cat subdomains.txt | python reptor simplelist -c upload --force-unlock  --num --header "My Heading" --level 4
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = 'simplelist'
        self.note_icon = '📃'
        self.arg_num = kwargs.get('num')
        self.arg_header = kwargs.get('header')
        self.arg_header_level = kwargs.get('level')

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        simplelist_parser = parser.add_argument_group()
        simplelist_parser.add_argument("--num",
                                        help="Create as numeric list",
                                        action="store_true",
                                        default=False)

        simplelist_parser.add_argument("--header",
                                        help="Set a header",
                                        action="store",
                                        default=None)

        simplelist_parser.add_argument("--level",
                                        help="Set a header level ",
                                        action="store",
                                        type=int,
                                        choices=[1,2,3,4,5,6],
                                        default=None)



    def parse(self):
        super().parse()

        if self.arg_header_level is not None and self.arg_header is None:
            # Todo: this is not possible because parser is not available.
            # With the current implementation we cannot have arguments
            # that require another argument to be present
            # parser.error("--level requires that you set --header")
            # current solution:
            print("--level requires --header to be present")
            exit()


        parsed_input = {
            'header': self.arg_header,
            'level': self.arg_header_level,
            "numeric": self.arg_num,
            'lines': []
        }

        for i, line in enumerate(self.raw_input.splitlines()):
            i += 1
            parsed_input['lines'].append({
                "id": i,
                "line": line
            })

        self.parsed_input = parsed_input

    def format(self):
        super().format()

        output = list()

        if self.parsed_input['header']:
            heading_level = "#"
            if self.parsed_input['level']:
                heading_level = "#" * self.parsed_input['level']
            output.append(f"{heading_level} {self.parsed_input['header']}")

        for item in self.parsed_input['lines']:
            if self.parsed_input['numeric']:
                output.append(f"{item['id']} {item['line']}")
            else:
                output.append(f"- {item['line']}")


        self.formatted_input = "\n".join(output)


loader = SimpleList
