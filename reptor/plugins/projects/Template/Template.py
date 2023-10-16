import json

from reptor.lib.plugins.Base import Base
from reptor.utils.table import make_table


class Template(Base):
    """
    Work with finding templates.
    """

    meta = {
        "name": "Template",
        "summary": "Queries Finding Templates from SysReptor",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg_search = kwargs.get("search")
        self.format: str = kwargs.get("format", "plain")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        templates_parsers = parser.add_argument_group()
        templates_parsers.add_argument(
            "--search", help="Search for term", action="store", default=None
        )
        templates_parsers.add_argument(
            "--json",
            help="Used with --search; output as json",
            action="store_const",
            dest="format",
            const="json",
            default="plain",
        )

    def run(self):
        if not self.arg_search:
            templates = self.reptor.api.templates.get_templates()
        else:
            templates = self.reptor.api.templates.search(self.arg_search)

        if self.format == "json":
            print(json.dumps([t.to_dict() for t in templates], indent=2))
        else:
            table = make_table(["Title", "Usage Count", "Tags", "Translations", "ID"])
            for template in templates:
                main_translation = [t for t in template.translations if t.is_main][0]
                table.add_row(
                    main_translation.data.title,
                    str(template.usage_count),
                    ",".join(template.tags),
                    ",".join(t.language for t in template.translations),
                    template.id,
                )

            self.console.print(table)


loader = Template
