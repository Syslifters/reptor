from unittest.mock import MagicMock

import pytest

from reptor.lib.reptor import Reptor

from ..ProjectsAPI import ProjectsAPI


class TestProjectsAPI:
    class MockedCheckResponse:
        check_response = {
            "messages": [
                {
                    "level": "warning",
                    "message": "Unresolved TODO",
                    "details": "TODO: Executive Summary**",
                    "location": {
                        "type": "section",
                        "id": "executive_summary",
                        "name": "Executive Summary",
                        "path": "executive_summary",
                    },
                },
                {
                    "level": "warning",
                    "message": "Unresolved TODO",
                    "details": "TODO company",
                    "location": {
                        "type": "section",
                        "id": "customer",
                        "name": "Customer",
                        "path": "customer_name",
                    },
                },
            ]
        }

        def json(self):
            return self.check_response

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config[
            "project_id"
        ] = "2b5de38d-2932-4112-b0f7-42c4889dd64d"
        self.project = ProjectsAPI(reptor=self.reptor)

    def test_render(self):
        class MockGenerateResponse:
            content = b"binary-data"

        self.project.check_report = MagicMock(
            return_value={
                "Unresolved TODO": self.MockedCheckResponse.check_response["messages"]
            }
        )
        self.project.post = MagicMock(return_value=MockGenerateResponse())
        self.project.log.warning = MagicMock()

        self.project.render()
        self.project.check_report.assert_called_once()
        self.project.post.assert_called_once()
        self.project.log.warning.assert_called_once_with(
            'Report Check Warning: "Unresolved TODO" (x2)'
        )

    def test_check_report(self):
        self.project.get = MagicMock(return_value=self.MockedCheckResponse())
        assert self.project.check_report() == self.MockedCheckResponse.check_response
        assert self.project.check_report(group_messages=True) == {
            "Unresolved TODO": self.MockedCheckResponse.check_response["messages"]
        }

    def test_project_api_init(self):
        # Test valid init
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config[
            "project_id"
        ] = "2b5de38d-2932-4112-b0f7-42c4889dd64d"
        try:
            ProjectsAPI(reptor=self.reptor).object_endpoint
        except ValueError:
            self.fail("ProjectsAPI raised ValueError")

        # Test missing server
        self.reptor._config._raw_config["server"] = ""
        with pytest.raises(ValueError):
            ProjectsAPI(reptor=self.reptor)

        # Test missing project id
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["project_id"] = ""
        with pytest.raises(ValueError):
            ProjectsAPI(reptor=self.reptor).object_endpoint
