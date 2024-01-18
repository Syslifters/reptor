import sys
from contextlib import nullcontext
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from requests.exceptions import HTTPError

from reptor.api.manager import APIManager
from reptor.lib.reptor import Reptor
from reptor.models.Project import Project
from reptor.models.ProjectDesign import ProjectDesign

from ..CreateProject import CreateProject


class TestCreateProject:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config[
            "project_id"
        ] = "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e"
        self.reptor._api = APIManager(reptor=self.reptor)

    def get_mocked_object(self):
        create_project = CreateProject(reptor=self.reptor)
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
        cp.run()
        cp.reptor.api.projects.create_project.assert_called_once_with(
            name="New Project created with Reptor",
            project_design="8a6ebd7b-1111-4f38-bfdd-3e8e9a24f64e",
            tags=["reptor"],
        )
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
