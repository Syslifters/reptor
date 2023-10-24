import json
import typing

import yaml

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
        self.export: typing.Optional[str] = kwargs.get("export")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        templates_parsers = parser.add_argument_group()
        templates_parsers.add_argument(
            "--search", help="Search for term", action="store", default=None
        )
        templates_parsers.add_argument(
            "--export",
            help="Export templates",
            choices=["tar.gz", "json", "yaml", "plain"],
            type=str.lower,
            action="store",
            dest="export",
            default=None,
        )

    def export_templates(
        self,
        template_ids: typing.List[str],
        format: typing.Optional[str] = "json",
        language: typing.Optional[str] = None,
    ):
        templates = list()
        for template_id in template_ids:
            templates.append(self.reptor.api.templates.get_template(template_id))
        if format == "json":
            print(json.dumps([t.to_dict() for t in templates], indent=2))
        elif format == "yaml":
            print(yaml.dump([t.to_dict() for t in templates]))
        elif format == "plain":
            for template in templates:
                for i, translation in enumerate(template.translations):
                    if i != 0:
                        self.print("")
                    if language and not translation.language.lower().startswith(
                        language
                    ):
                        continue
                    translation_data = translation.data.to_dict()
                    self.console.print(
                        f"[bold][red]{translation_data.pop('title')} ({translation.language})[/red][/bold]"
                    )
                    for key, value in translation_data.items():
                        if value:
                            if isinstance(value, list):
                                if len(value) > 1:
                                    value = "\n".join(
                                        ["* " + item.__str__() for item in value]
                                    )
                                elif len(value) == 1:
                                    value = value[0]
                            self.console.print(
                                f"[bold][blue]{key} ({translation.language})[/blue][/bold]"
                            )
                            self.print(value.__str__())
                            self.print("")

    def run(self):
        if not self.arg_search:
            templates = self.reptor.api.templates.get_template_overview()
        else:
            templates = self.reptor.api.templates.search(self.arg_search)

        if self.export == "tar.gz":
            pass
        elif self.export:
            self.export_templates([t.id for t in templates], format=self.export)
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
