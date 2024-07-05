from uuid import UUID

from requests.exceptions import HTTPError

from reptor.lib.plugins.UploadBase import UploadBase


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


    def run(self):
        if self.template_id:
            try:
                UUID(self.template_id)
            except ValueError:
                self.log.error(f'template_id "{self.template_id}" is not a UUID')
                return
            try:
                template = self.reptor.api.templates.get_template(self.template_id)
            except HTTPError as e:
                if e.response.status_code == 404:
                    self.log.error(f"Template with ID {self.template_id} doesn't exist")
                    return
                else:
                    self.log.error(f"Failed to get template: {e}")
                    return
            upload_templates = [template]
        elif self.tags:
            templates = [
                t
                for tag in self.tags
                for t in self.reptor.api.templates.get_templates_by_tag(tag)
            ]
            upload_templates = list()
            upload_template_ids = set()
            for template in templates:
                if template.id in upload_template_ids:
                    continue
                if all(tag in template.tags for tag in self.tags):
                    upload_templates.append(template)
                    upload_template_ids.add(template.id)
            if not upload_templates:
                self.log.error(f"No templates found with tags: {', '.join(self.tags)}")
                return
        else:
            self.log.error("No template_id or tags provided (use --template-id or --tags)")
            return

        for template in upload_templates:
            if any(
                t.language == self.reptor.api.projects.project.language
                for t in template.translations
            ):
                language = self.reptor.api.projects.project.language
                template_title = [t.data.title for t in template.translations if t.language == language][0]
            else:
                language = None
                template_title = template.translations[0].data.title
            
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
                    self.log.error(
                        f'Failed to create finding from template "{template_title}": {e}'
                    )
                    continue

            self.success(
                f'Successfully created finding "{template_title}"'
            )

loader = FindingFromTemplate
