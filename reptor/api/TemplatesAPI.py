import typing
from posixpath import join as urljoin

from reptor.api.APIClient import APIClient
from reptor.models.FindingTemplate import FindingTemplate


class TemplatesAPI(APIClient):
    """API client for interacting with SysReptor finding templates.

    Example:
        ```python
        from reptor import Reptor

        reptor = Reptor(
            server=os.environ.get("REPTOR_SERVER"),
            token=os.environ.get("REPTOR_TOKEN"),
        )

        # TemplatesAPI is available as reptor.api.templates, e.g.:
        reptor.api.templates.search()
        ```
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = urljoin(
            self.reptor.get_config().get_server(), "api/v1/findingtemplates/"
        )

    def get_template(self, template_id: str) -> FindingTemplate:
        """Gets a finding template by ID.

        Args:
            template_id (str): Finding template ID

        Returns:
            The FindingTemplate object with all its data

        Example:
            ```python
            reptor.api.templates.get_template("123e4567-e89b-12d3-a456-426614174000")
            ```
        """
        response = self.get(urljoin(self.base_endpoint, template_id))
        return FindingTemplate(response.json())

    def search(self, search_term: str = "") -> typing.List[FindingTemplate]:
        """Searches through the templates using a search term.

        Args:
            search_term (str, optional): Term to search in finding templates. 
                                       Defaults to empty string which returns all templates.

        Returns:
            List of templates matching the search criteria

        Example:
            ```python
            reptor.api.templates.search("SQL Injection")
            ```
        """
        templates_raw = self.get_paginated(self.base_endpoint, params={"search": search_term})
        return [FindingTemplate(template_raw) for template_raw in templates_raw]

    def upload_template(
        self, template: FindingTemplate
    ) -> typing.Optional[FindingTemplate]:
        """Uploads a new Finding Template.

        Args:
            template (FindingTemplate): The template model data to upload

        Returns:
            The uploaded template with server-assigned ID, or None if a template with the same title already exists

        Example:
            ```python
            new_template = FindingTemplate(template_data)
            uploaded = reptor.api.templates.upload_template(new_template)
            if uploaded:
                print(f"Template uploaded with ID: {uploaded.id}")
            ```
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

    def update_template(
        self, template_id: str, template: FindingTemplate
    ) -> FindingTemplate:
        """Updates an existing finding template using a PATCH request.

        Args:
            template_id (str): Finding template ID to update
            template (FindingTemplate): The template model data with updated fields

        Returns:
            The updated FindingTemplate object

        Example:
            ```python
            template = reptor.api.templates.get_template("123e4567-e89b-12d3-a456-426614174000")
            template.translations[0].data.title = "Updated Title"
            updated = reptor.api.templates.update_template(template.id, template)
            ```
        """
        res = self.patch(
            urljoin(self.base_endpoint, template_id),
            json=template.to_dict(),
        )
        return FindingTemplate(res.json())

    def delete_template(self, template_id: str) -> None:
        """Deletes a finding template by ID.

        Args:
            template_id (str): Finding template ID

        Returns:
            :

        Example:
            ```python
            reptor.api.templates.delete_template("123e4567-e89b-12d3-a456-426614174000")
            ```
        """
        self.delete(urljoin(self.base_endpoint, template_id))
        return

    def export(self, template_id: str) -> bytes:
        """Exports a template in archive format (tar.gz).

        Args:
            template_id (str): Finding template ID

        Returns:
            The template archive content as bytes

        Example:
            ```python
            archive_data = reptor.api.templates.export("123e4567-e89b-12d3-a456-426614174000")
            with open("template.tar.gz", "wb") as f:
                f.write(archive_data)
            ```
        """
        url = urljoin(self.base_endpoint, f"{template_id}/export/")
        return self.post(url).content

    def get_templates_by_tag(self, tag: str) -> typing.List[FindingTemplate]:
        """Retrieves templates that contain a specific tag.

        Args:
            tag (str): The tag to search for in template tags

        Returns:
            List of templates that contain the specified tag

        Example:
            ```python
            web_templates = reptor.api.templates.get_templates_by_tag("web")
            print(f"Found {len(web_templates)} web-related templates")
            ```
        """
        matched_templates = list()
        for finding_template in self.search(tag):
            if tag in finding_template.tags:
                matched_templates.append(finding_template)
        return matched_templates
        return matched_templates
