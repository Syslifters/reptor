import typing
from posixpath import join as urljoin

from reptor.api.APIClient import APIClient
from reptor.models.FindingTemplate import FindingTemplate


class TemplatesAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = urljoin(
            self.reptor.get_config().get_server(), f"api/v1/findingtemplates/"
        )

    def get_template(self, template_id: str) -> FindingTemplate:
        """Gets a single Template by ID"""
        response = self.get(urljoin(self.base_endpoint, template_id))
        return FindingTemplate(response.json())

    def export(self, template_id: str) -> bytes:
        """Exports a template in archive format (tar.gz)"""
        url = urljoin(self.base_endpoint, f"{template_id}/export/")
        return self.post(url).content

    def search(self, search_term: str = "") -> typing.List[FindingTemplate]:
        """Searches through the templates"""
        templates_raw = self.get_paginated(self.base_endpoint, params={"search": search_term})
        return [FindingTemplate(template_raw) for template_raw in templates_raw]

    def get_templates_by_tag(self, tag: str) -> typing.List[FindingTemplate]:
        matched_templates = list()
        for finding_template in self.search(tag):
            if tag in finding_template.tags:
                matched_templates.append(finding_template)
        return matched_templates

    def upload_template(
        self, template: FindingTemplate
    ) -> typing.Optional[FindingTemplate]:
        """Uploads a new Finding Template to API

        Args:
            template (FindingTemplate): Model Data to upload

        Returns:
            FindingTemplate: Updated Model with ID etc.
        """
        existing_templates = self.search(template.translations[0].data.title)
        if any([t.translations[0].data.title == template.translations[0].data.title for t in existing_templates]):
            self.display(f"Template with title {template.translations[0].data.title} exists. Skipping.")
            return None
        
        res = self.post(
            self.base_endpoint,
            json=template.to_dict(),
        )
        return FindingTemplate(res.json())


    def delete_template(self, template_id: str) -> None:
        """Deletes a Template by ID"""
        self.delete(urljoin(self.base_endpoint, template_id))
        return
