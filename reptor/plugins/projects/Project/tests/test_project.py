import sys
from unittest.mock import MagicMock

import pytest

from reptor.api.manager import APIManager
from reptor.lib.reptor import Reptor

from ..Project import Project


class TestProject:
    @pytest.fixture(autouse=True)
    def setUp(self):
        reptor = Reptor()
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
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
        self.project.print = MagicMock()
        sys.stdout.buffer.write = MagicMock()
        self.project.reptor.api.projects.post = MagicMock(return_value=MockResponse())
        self.project.reptor.api.projects.project.to_dict = MagicMock(
            return_value={"a": "b"}
        )

        if format == "archive":
            assert self.project._export_project(format=format, filename=None) is None
            sys.stdout.buffer.write.assert_not_called()

            assert self.project._export_project(format=format, filename="-") is None
            sys.stdout.buffer.write.assert_called_once_with(expected)
        else:
            assert self.project._export_project(format=format, filename=None) is None
            self.project.print.assert_called_once_with(expected)
