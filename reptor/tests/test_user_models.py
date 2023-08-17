import json

from reptor.models.User import User


class TestUserModelParsing:
    example_user = """
{
            "id": "e79abf41-5b7c-4c1f-826e-040f34eaf6b4",
            "created": "2023-05-19T08:19:23.679429Z",
            "updated": "2023-05-19T08:19:23.680725Z",
            "last_login": null,
            "is_active": true,
            "username": "rs",
            "name": "Richard Schwabe",
            "title_before": null,
            "first_name": "Richard",
            "middle_name": null,
            "last_name": "Schwabe",
            "title_after": null,
            "email": null,
            "phone": null,
            "mobile": null,
            "scope": [
                "admin",
                "template_editor",
                "designer",
                "user_manager"
            ],
            "is_superuser": true,
            "is_designer": false,
            "is_template_editor": false,
            "is_user_manager": false,
            "is_guest": false,
            "is_system_user": false,
            "is_global_archiver": false,
            "is_mfa_enabled": false,
            "can_login_local": true,
            "can_login_sso": false
        }
        """

    def test_user_parsing(self):
        api_test_data = json.loads(self.example_user)

        test_user = User(api_test_data)

        assert test_user.id == "e79abf41-5b7c-4c1f-826e-040f34eaf6b4"
        assert test_user.name == "Richard Schwabe"
        assert test_user.first_name == "Richard"
        assert test_user.last_name == "Schwabe"
        assert test_user.is_superuser == True
        assert test_user.scope
