import typing
from uuid import UUID

from requests.exceptions import HTTPError

from reptor.lib.plugins.UploadBase import UploadBase
from reptor.models.FindingTemplate import FindingTemplate


class FindingFromTemplate(UploadBase):
    meta = {
        "name": "FindingFromTemplate",
        "summary": "Creates findings from remote finding templates",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_id = kwargs.get("template_id", None)
        self.tags = (kwargs.get("tags") or "").split(",")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)
        action_group = parser.add_argument_group()
        action_group.add_argument(
            "--template-id",
            metavar="TEMPLATE_ID",
            action="store",
            nargs="?",
            help="UUID of the template to use",
        )
        action_group.add_argument(
            "--tags",
            metavar="TAGS",
            action="store",
            help="Create findings from finding templates with the specified tags; comma-separated list of tags",
        )


    def _get_template_by_id(self, template_id) -> FindingTemplate:
        try:
            UUID(template_id)
        except ValueError:
            raise ValueError(f'template_id "{template_id}" is not a UUID')
        try:
            template = self.reptor.api.templates.get_template(template_id)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise KeyError(f"Template with ID {template_id} doesn't exist")
            else:
                raise HTTPError(f"Failed to get template: {e}") from e
        return template

    def _get_templates_by_tags(self, tags) -> typing.List[FindingTemplate]:
        templates = [
            t
            for tag in tags
            for t in self.reptor.api.templates.get_templates_by_tag(tag)
        ]
        upload_templates = list()
        upload_template_ids = set()
        for template in templates:
            if template.id in upload_template_ids:
                continue
            if all(tag in template.tags for tag in tags):
                upload_templates.append(template)
                upload_template_ids.add(template.id)
        if not upload_templates:
            raise KeyError(f"No templates found with tags: {', '.join(tags)}")
        return upload_templates


    def _get_template_translation(self, finding_template: FindingTemplate) -> typing.Tuple[int, str]:
        for i, t in enumerate(finding_template.translations):
            if t.language == self.reptor.api.projects.project.language:
                break
        else:
            for i, t in enumerate(finding_template.translations):
                if t.is_main:
                    return i, t.language
        return i, t.language


    def run(self):
        if self.template_id:
            upload_templates = [self._get_template_by_id(self.template_id)]
        elif self.tags:
            upload_templates = self._get_templates_by_tags(self.tags)
        else:
            raise ValueError("No template_id or tags provided (use --template-id or --tags)")

        for template in upload_templates:
            translation_index, language = self._get_template_translation(template)
            template_title = template.translations[translation_index].data.title
            
            if template.id in [f.template for f in self.reptor.api.projects.project.findings]:
                self.display(
                    f'Skipping template "{template_title}" as it already exists in the project'
                )
                continue
            
            try:
                self.reptor.api.projects.create_finding_from_template(template.id, language=language)
            except HTTPError as e:
                if template_msgs := e.response.json().get("template", list()):
                    template_msg = '\n'.join(template_msgs)
                    self.log.error(
                        f"{template_msg}"
                    )
                else:
                    raise Exception(f'Failed to create finding from template "{template_title}": {e}')

            self.success(
                f'Successfully created finding "{template_title}"'
            )

loader = FindingFromTemplate
