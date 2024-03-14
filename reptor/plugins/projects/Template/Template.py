import contextlib
import io
import json
import sys
import tarfile
import typing

import tomli
import yaml

from reptor.lib.plugins.Base import Base
from reptor.models.FindingTemplate import FindingTemplate
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
        self.list = kwargs.get("list")
        self.export: typing.Optional[str] = kwargs.get("export")
        self.language: typing.Optional[str] = kwargs.get("language")
        self.output: typing.Optional[str] = kwargs.get("output")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        templates_parsers = parser.add_argument_group()
        templates_parsers.add_argument(
            "--list",
            help="List all finding templates",
            action="store_true",
            default=False,
        )
        templates_parsers.add_argument(
            "--search", help="Search for term", action="store", default=None
        )
        templates_parsers.add_argument(
            "--language",
            help='Template language for export format "plain", e.g. "en"',
            action="store",
            default=None,
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
        parser.add_argument(
            "-o",
            "--output",
            metavar="FILENAME",
            help="Filename for output",
            action="store",
            default=None,
        )

    def _merge_tars(self, tars: typing.Iterable) -> bytes:
        result_io = io.BytesIO()
        with tarfile.open(fileobj=result_io, mode="w:gz") as result_tar:
            for tar in tars:
                tar = io.BytesIO(tar)
                with tarfile.open(fileobj=tar, mode="r:gz") as tar_file:
                    for member in tar_file.getmembers():
                        if member.isdir():
                            result_tar.addfile(member)
                        else:
                            result_tar.addfile(member, tar_file.extractfile(member))
        result_io.seek(0)
        return result_io.read()

    def export_archive(
        self,
        template_ids: typing.List[str],
        filename: str,
        stdout: bool = False,
    ):
        tar = self._merge_tars(
            ((self.reptor.api.templates.export(id) for id in template_ids))
        )
        self.deliver_file(
            content=tar,
            filename=filename,
            upload=False,
            stdout=stdout,
        )
        return

    def export_templates(
        self,
        template_ids: typing.List[str],
        format: typing.Optional[str] = "json",
        language: typing.Optional[str] = None,
        filename: typing.Optional[str] = None,
        stdout: bool = True,
    ):
        if format == "plain" and not stdout:
            raise ValueError('"plain" can only be used with stdout')
        templates = list()
        output = ""
        for template_id in template_ids:
            templates.append(self.reptor.api.templates.get_template(template_id))
        if format == "json":
            output = json.dumps([t.to_dict() for t in templates], indent=2)
        elif format == "yaml":
            output = yaml.dump([t.to_dict() for t in templates])
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
            return

        self.deliver_file(
            content=output.encode(),
            filename=filename or "",
            upload=False,
            stdout=stdout,
        )

    def _read_finding_templates(
        self, content: typing.Optional[str] = None
    ) -> typing.Iterator[FindingTemplate]:
        if content is None:
            # Read finding from stdin
            self.display("Reading from stdin...")
            content = sys.stdin.read()

        loaded_content: typing.Union[None, dict, list] = None
        with contextlib.suppress(json.JSONDecodeError):
            loaded_content = json.loads(content, strict=False)
        if not loaded_content:
            with contextlib.suppress(tomli.TOMLDecodeError):
                loaded_content = tomli.loads(content)
        if not loaded_content:
            raise ValueError("Could not decode stdin (expected JSON or TOML)")

        if isinstance(loaded_content, dict):
            loaded_content = [loaded_content]

        for finding_template in loaded_content:
            assert isinstance(finding_template, dict)
            yield FindingTemplate(finding_template)

    def run(self):
        filename = self.output
        if self.list:
            templates = self.reptor.api.templates.get_template_overview()
        elif self.arg_search:
            templates = self.reptor.api.templates.search(self.arg_search)
        else:
            i = None
            for i, finding_template in enumerate(self._read_finding_templates()):
                new = self.reptor.api.templates.upload_template(finding_template)
                self.log.display(
                    f'Uploaded finding template "{new.translations[0].data.title}" with new ID {new.id}'
                )
            if i is not None:
                self.log.success(
                    f"Successfully uploaded {i+1} finding template{'s'[:i^1]}"
                )
            return

        if not templates:
            self.display("Did not find any finding templates.")
            return

        if self.export == "tar.gz":
            stdout = False
            if self.output == "-":
                stdout = True
            if len(templates) == 1 and not self.output:
                filename = (
                    f"{templates[0].translations[0].data.title or 'template'}.tar.gz"
                )
            else:
                filename = "templates.tar.gz"
            self.export_archive(
                [t.id for t in templates], filename=filename, stdout=stdout
            )
        elif self.export:
            stdout = True
            if self.output == "-" or self.output is None:
                filename = None
            elif self.output:
                stdout = False
                filename = self.output
            self.export_templates(
                [t.id for t in templates],
                format=self.export,
                language=self.language,
                filename=filename,
                stdout=stdout,
            )
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
