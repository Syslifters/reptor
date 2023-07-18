from reptor.lib.plugins.Base import Base
from reptor.api.TemplatesAPI import TemplatesAPI

from reptor.utils.table import make_table


class Templates(Base):
    """
    Work with the finding templates.
    """

    meta = {
        "name": "Templates",
        "summary": "Queries Finding Templates from reptor.api",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_search = kwargs.get("search")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath)
        templates_parsers = parser.add_argument_group()
        templates_parsers.add_argument(
            "--search", help="Search for term", action="store", default=None
        )

    def run(self):
        if not self.arg_search:
            templates = self.reptor.api.templates.get_templates()
        else:
            templates = self.reptor.api.templates.search(self.arg_search)

        table = make_table(["Title", "ID"])
        for template in templates:
            finding = template.data
            if finding:
                table.add_row(finding.title, template.id)
            else:
                self.console.print(
                    f"Template [yellow]{template.id}[/yellow] has no finding data."
                )

        self.console.print(table)


loader = Templates
