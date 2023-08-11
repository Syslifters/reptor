import typing
from posixpath import join as urljoin

from reptor.api.APIClient import APIClient
from reptor.api.models import FindingTemplate


class TemplatesAPI(APIClient):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.base_endpoint = urljoin(
            self.reptor.get_config().get_server(), f"api/v1/findingtemplates/"
        )
        self.object_endpoint = urljoin(f"api/v1/findingtemplates/{self.project_id}")

    def get_templates(self) -> typing.List[FindingTemplate]:
        """Gets list of Templates"""
        response = self.get(self.base_endpoint)
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(FindingTemplate(item))
        return return_data

    def search(self, search_term) -> typing.List[FindingTemplate]:
        """Searches through the templates"""

        response = self.get(urljoin(self.base_endpoint, f"?search={search_term}"))
        return_data = list()
        for item in response.json()["results"]:
            return_data.append(FindingTemplate(item))
        return return_data

    def upload_new_template(
        self, template: object, language: str, tags: typing.Optional[list] = None
    ) -> typing.Optional[FindingTemplate]:
        """Uploads a new Finding Template to API

        Args:
            template (FindingTemplate): Model Data to upload

        Returns:
            FindingTemplate: Updated Model with ID etc.
        """
        # template.data._to_api_json()
        return_template = None
        res = self.post(
            self.base_endpoint,
            data={
                "tags": tags or [],
                "translations": [
                    {
                        "status": "in-progress",
                        "language": language,
                        "is_main": True,  # New templates are always main language
                        "data": {
                            "title": template.data.title,
                        },
                    }
                ],
            },
        )
        raw_data = res.json()
        self.debug(raw_data)
        if raw_data:
            updated_template = FindingTemplate(raw_data)
            updated_template.data = template.data
            translations = [t.__dict__ for t in updated_template.translations]
            for t in translations:
                t.update(
                    {
                        "data": t.get("data").__dict__
                        if not t.get("is_main")
                        else updated_template.data._to_api_json(),
                    }
                )
            updated_data = {
                "id": updated_template.id,
                "translations": translations,
            }
            self.debug(updated_data)
            self.put(
                f"{self.base_endpoint}{updated_template.id}",
                updated_data,
            )
            return_template = updated_template

        return return_template
