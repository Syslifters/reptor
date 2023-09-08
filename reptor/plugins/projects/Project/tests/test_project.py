from unittest.mock import MagicMock

import pytest

from reptor.api.manager import APIManager
from reptor.lib.reptor import Reptor

from ..Project import Project


class TestProject:
    @pytest.fixture(autouse=True)
    def setUp(self):
        reptor = Reptor()
        reptor._config._raw_config[
            "project_id"
        ] = "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e"
        reptor._api = APIManager(reptor=reptor)
        self.project = Project(reptor=reptor)

    @pytest.mark.parametrize(
        "format,expected",
        [
            ("archive", b"binary-data"),
            ("json", '{\n  "a": "b"\n}'),
            ("toml", 'a = "b"\n'),
            ("yaml", "a: b\n"),
        ],
    )
    def test_export_project(self, format, expected):
        class MockResponse:
            content = b"binary-data"

        # self.project.reptor.api.projects.export = MagicMock()
        self.project.reptor.api.projects.project = MagicMock()
        self.project.console.print = MagicMock()
        self.project.reptor.api.projects.console.print = MagicMock()
        self.project.reptor.api.projects.post = MagicMock(return_value=MockResponse())
        self.project.reptor.api.projects.project.to_dict = MagicMock(
            return_value={"a": "b"}
        )

        assert self.project._export_project(format=format, filename=None) is None
        self.project.console.print.assert_called_once_with(expected)
