from reptor.lib.modules.Base import Base
from reptor.api.TemplatesAPI import TemplatesAPI

from reptor.lib.console import reptor_console
from reptor.utils.table import make_table


class Templates(Base):
    """
    Author: Syslifters
    Website: https://github.com/Syslifters/reptor

    Short Help:
    Queries Finding Templates from reptor.api
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_search = kwargs.get("search")

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        templates_parsers = parser.add_argument_group()
        templates_parsers.add_argument(
            "--search", help="Search for term", action="store", default=None
        )

    def run(self):
        template_api: TemplatesAPI = TemplatesAPI(self.reptor)
        if not self.arg_search:
            templates = template_api.get_templates()
        else:
            templates = template_api.search(self.arg_search)

        table = make_table(["Title", "ID"])
        for template in templates:
            finding = template.data
            if finding:
                table.add_row(finding.title, template.id)
            else:
                reptor_console.print(
                    f"Template [yellow]{template.id}[/yellow] has no finding data."
                )

        reptor_console.print(table)


loader = Templates
