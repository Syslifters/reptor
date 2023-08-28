import json

from reptor.models.Finding import Finding
from reptor.models.Project import Project
from reptor.models.Section import Section
from reptor.models.User import User


class TestProjectModelParsing:
    example_project = """
    {
            "id": "4cf78324-8502-4fb0-936a-724892d3c539",
            "created": "2023-06-16T19:12:00.478314Z",
            "updated": "2023-06-25T13:49:48.935500Z",
            "name": "PNPT Exam",
            "project_type": "fa670018-e6ef-4b73-989b-1e4c4af09cee",
            "language": "en-US",
            "tags": [],
            "readonly": true,
            "source": "created",
            "copy_of": null,
            "members": [
                {
                    "id": "f2c9bad4-c916-4c18-9f76-d5ef94b34453",
                    "username": "reptor",
                    "name": "Bjoern Schwabe",
                    "title_before": "",
                    "first_name": "Bjoern",
                    "middle_name": null,
                    "last_name": "Schwabe",
                    "title_after": "",
                    "is_active": true,
                    "roles": [
                        "pentester"
                    ]
                },
                {
                    "id": "f2c9bad4-c916-4c18-9f76-d5ef94b34454",
                    "username": "richard",
                    "name": "Richard Schwabe",
                    "title_before": "",
                    "first_name": "Richard",
                    "middle_name": null,
                    "last_name": "Schwabe",
                    "title_after": "",
                    "is_active": true,
                    "roles": [
                        "pentester"
                    ]
                }
            ],
            "imported_members": [],
            "details": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539",
            "findings": [{"id": "a9e6fd6b-773f-46a8-8a5c-58fdeefbdfc0", "created": "2023-08-25T11:57:03.886931Z", "updated": "2023-08-25T11:57:03.889063Z", "project": "4820bd5d-51f1-4dca-a4a4-78ba935b615c", "project_type": "50dfad6e-805d-4215-b098-a73e03b1ec3b", "language": "en-US", "lock_info": null, "template": null, "assignee": null, "status": "in-progress", "order": 1, "data": {"cvss": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N", "title": "Reflected Cross-Site Scripting (XSS)", "impact": "", "summary": "We detected a reflected XSS vulnerability.\\n\\n**XSS targets**\\n\\n* https://example.com/alert(1)\\n* https://example.com/q=alert(1)\\n", "severity": null, "references": ["https://owasp.org/www-community/attacks/xss/"], "description": "", "precondition": "", "retest_notes": "", "retest_status": null, "wstg_category": null, "recommendation": "HTML encode user-supplied inputs.", "owasp_top10_2021": null, "affected_components": ["https://example.com/alert(1)", "https://example.com/q=alert(1)"], "short_recommendation": ""}}],
            "sections": [{"id": "other", "label": "Executive Summary", "fields": ["title"], "project": "4820bd5d-51f1-4dca-a4a4-78ba935b615c", "project_type": "50dfad6e-805d-4215-b098-a73e03b1ec3b", "language": "en-US", "lock_info": null, "assignee": null, "status": "in-progress", "data": {"title": "Test"}}],
            "notes": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539/notes",
            "images": "http://localhost:8000/api/v1/pentestprojects/4cf78324-8502-4fb0-936a-724892d3c539/images"
        }"""

    def test_project_parsing(self):
        api_test_data = json.loads(self.example_project)

        test_project = Project(api_test_data)
        assert test_project.id == "4cf78324-8502-4fb0-936a-724892d3c539"
        assert test_project.members[0].id == "f2c9bad4-c916-4c18-9f76-d5ef94b34453"
        assert test_project.members[1].username == "richard"
        assert test_project.project_type == "fa670018-e6ef-4b73-989b-1e4c4af09cee"

        assert isinstance(test_project.sections[0], Section)
        assert isinstance(test_project.findings[0], Finding)
        assert isinstance(test_project.members[0], User)

        test_project_dict = test_project.to_dict()
        # Ensure items are still as before to_dict
        assert isinstance(test_project.sections[0], Section)
        assert isinstance(test_project.findings[0], Finding)
        assert isinstance(test_project.members[0], User)

        assert isinstance(test_project_dict["sections"], list)
        assert isinstance(test_project_dict["findings"], list)
        assert isinstance(test_project_dict["members"], list)

        assert (
            test_project.findings[0].data.title.value
            == "Reflected Cross-Site Scripting (XSS)"
        )
        assert test_project.sections[0].data.title.value == "Test"

        assert (
            test_project_dict["findings"][0]["data"]["title"]
            == "Reflected Cross-Site Scripting (XSS)"
        )
        assert test_project_dict["sections"][0]["data"]["title"] == "Test"
