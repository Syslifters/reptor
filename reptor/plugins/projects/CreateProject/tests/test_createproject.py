from unittest.mock import MagicMock

import pytest

from reptor.api.manager import APIManager
from reptor.lib.reptor import reptor
from reptor.models.Project import Project
from reptor.models.ProjectDesign import ProjectDesign

from ..CreateProject import CreateProject


class TestCreateProject:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = reptor
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["project_id"] = (
            "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e"
        )
        self.reptor._api = APIManager(reptor=self.reptor)

    def get_mocked_object(self):
        create_project = CreateProject()
        create_project.design = "8a6ebd7b-1111-4f38-bfdd-3e8e9a24f64e"
        create_project.reptor.api.projects.create_project = MagicMock()
        create_project.reptor.api.projects.create_project.return_value = Project(
            {"id": "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e"},
            ProjectDesign(),
        )
        self.reptor._config._write_to_file = MagicMock()
        self.reptor._config.load_config = MagicMock()
        self.reptor._config.load_config.return_value = {
            "server": "https://demo.sysre.pt",
            "project_id": "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e",
        }
        return create_project

    def test_create_project(self):
        cp = self.get_mocked_object()
        create_project_mock = cp.reptor.api.projects.create_project
        cp.run()
        create_project_mock.assert_called_once_with(
            name="New Project created with Reptor",
            project_design="8a6ebd7b-1111-4f38-bfdd-3e8e9a24f64e",
            tags=["reptor"],
        )
        if cp.reptor._config._no_config_file:
            cp.reptor._config._write_to_file.assert_not_called()
        else:
            cp.reptor._config._write_to_file.assert_called_once_with(
                config={
                    "server": "https://demo.sysre.pt",
                    "project_id": "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e",
                }
            )

    def test_create_project_no_update_config(self):
        cp = self.get_mocked_object()
        cp.no_update_config = True
        cp.run()
        cp.reptor.api.projects.create_project.assert_called_once_with(
            name="New Project created with Reptor",
            project_design="8a6ebd7b-1111-4f38-bfdd-3e8e9a24f64e",
            tags=["reptor"],
        )
        cp.reptor._config._write_to_file.assert_not_called()
