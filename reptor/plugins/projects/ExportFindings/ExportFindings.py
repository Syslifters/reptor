import csv
import io
import json
import typing

import cvss
import tomli_w
import yaml

from reptor.lib.plugins.Base import Base


class ExportFindings(Base):
    """
    Export your project findings as a summary or checklist.
    """

    meta = {
        "name": "ExportFindings",
        "summary": "Export your project findings as a summary or checklist",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.format: str = kwargs.get("export", "")
        self.output: typing.Optional[str] = kwargs.get("output")
        self.upload: bool = kwargs.get("upload", False)
        self.fieldnames: str = kwargs.get("fieldnames", "").split(",")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        parser.add_argument(
            "--format",
            help="Output format",
            choices=["csv", "json", "toml", "yaml"],
            type=str.lower,
            action="store",
            dest="export",
            default="csv",
        )
        parser.add_argument(
            "--fieldnames",
            help="Fieldnames to be included, comma-separated",
            action="store",
            default="retest_status,title,affected_components,cvss",
        )
        parser.add_argument(
            "-o",
            "--output",
            metavar="FILENAME",
            help="Filename to store output, empty for stdout",
            action="store",
            default=None,
        )
        parser.add_argument(
            "--upload",
            action="store_true",
            help="Used with --export or --render; uploads file to note",
            dest="upload",
        )

    def _findings_summary(self, format="csv", filename=None, upload=False):
        stdout = False
        default_filename = self.reptor.api.projects.project.name or "project"
        if filename in ["-", None] and not upload:
            stdout = True
            filename = None

        findings = list()
        for finding in self.reptor.api.projects.project.findings:
            finding_summary = dict()
            for field in self.fieldnames:
                try:
                    finding_field = getattr(finding.data, field)
                except AttributeError:
                    finding_summary[field] = ""
                    continue
                finding_summary[field] = finding_field.value

                # Retest status if empty
                if field == "retest_status" and not finding_summary[field]:
                    finding_summary[field] = "Open"

                # Join lists
                if isinstance(finding_summary[field], list):
                    finding_summary[field] = ", ".join(
                        f.value for f in finding_summary[field]
                    )

                # Calculate CVSS
                if finding_field.type == "cvss":
                    finding_summary[f"{field}__score"] = ""
                    finding_summary[f"{field}__severity"] = ""
                    finding_summary[f"{field}__vector"] = ""
                    vector = finding_summary.pop(field)
                    try:
                        cvss_metrics = cvss.CVSS3(vector)

                    except (cvss.exceptions.CVSS3MalformedError, IndexError):
                        try:
                            cvss_metrics = cvss.CVSS2(vector)
                            finding_summary[f"{field}__severity"] = (
                                cvss_metrics.severities()[-1]
                            )
                        except (cvss.exceptions.CVSS2MalformedError, IndexError):
                            cvss_metrics = None
                    if cvss_metrics:
                        finding_summary[f"{field}__score"] = (
                            cvss_metrics.environmental_score
                        )
                        finding_summary[f"{field}__vector"] = vector
                        finding_summary[f"{field}__severity"] = (
                            cvss_metrics.severities()[-1]
                        )
            findings.append(finding_summary)

        output = ""
        if format == "json":
            output = json.dumps(findings, indent=2)
        elif format == "toml":
            output = tomli_w.dumps(findings)  # type: ignore
        elif format == "yaml":
            output = yaml.dump(findings)
        elif format == "csv":
            with io.StringIO() as csvfile:
                headers = self.fieldnames
                if findings:
                    headers = list(findings[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for row in findings:
                    writer.writerow(row)
                output = csvfile.getvalue()
        else:
            raise ValueError(f"Unknown format: {format}")
        self.deliver_file(
            content=output.encode(),
            filename=filename or f"{default_filename}.{format}",
            upload=upload,
            stdout=stdout,
        )

    def run(self):
        self._findings_summary(self.format, filename=self.output, upload=self.upload)


loader = ExportFindings
