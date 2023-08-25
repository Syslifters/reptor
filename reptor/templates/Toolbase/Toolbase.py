from reptor.lib.plugins.ToolBase import ToolBase


class MYMODULENAME(ToolBase):
    """
    Author: AUTHOR_NAME
    Version: 1.0
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: TAGS_LIST

    Short Help:
    Please provide a short description, that is shown in the modules overview

    Description:

    You can provide a long description here, that will also be shown in the official a documentation,
    if you wish to make this a community module.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notename = kwargs.get("notename", "MYMODULENAME")
        self.note_icon = "📃"
        self.arg_foo = kwargs.get("foo")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        """Any arguments added in here are accessible via kwargs in the constructor"""
        super().add_arguments(parser, plugin_filepath=plugin_filepath)

        # Simple Toggle
        parser.add_argument(
            "--foo", help="Create as numeric list", action="store_true", default=False
        )

        # Simple Integer only valid from a selection of integers
        parser.add_argument(
            "--bar",
            help="More complex example",
            action="store",
            type=int,
            choices=[1, 2, 3, 4, 5, 6],
            default=None,
        )

    def parse_xml(self, xml_root):
        """This is called automatically if the user provices --format xml
        For more infos look at the parent parse() method in ToolBase
        """
        super().parse_xml()

    def parse_json(self):
        """This is called automatically if the user provices --format json
        For more infos look at the parent parse() method in ToolBase
        """
        super().parse_json()

    def parse_csv(self):
        """This is called automatically if the user provices --format csv
        For more infos look at the parent parse() method in ToolBase
        """
        ...

    def process_parsed_input_for_template(self):
        return super().process_parsed_input_for_template()


loader = MYMODULENAME
