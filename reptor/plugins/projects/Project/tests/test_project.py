import sys
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from requests.exceptions import HTTPError
from contextlib import nullcontext
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
        "filename,upload,expected_kwargs",
        [
            (
                "test.tar.gz",
                False,
                {
                    "content": b"binary-data",
                    "filename": "test.tar.gz",
                    "upload": False,
                    "stdout": False,
                },
            ),
            (
                "test.tar.gz",
                True,
                {
                    "content": b"binary-data",
                    "filename": "test.tar.gz",
                    "upload": True,
                    "stdout": False,
                },
            ),
            (
                "-",
                True,
                {
                    "content": b"binary-data",
                    "filename": "my-project.tar.gz",
                    "upload": True,
                    "stdout": True,
                },
            ),
        ],
    )
    def test_export_archive(self, filename, upload, expected_kwargs):
        self.project.deliver_file = MagicMock()
        archive_data = b"binary-data"
        self.project.reptor.api.projects.export = MagicMock(return_value=archive_data)
        self.project.reptor.api.projects.project = MagicMock()
        self.project.reptor.api.projects.project.name = "my-project"

        self.project._export_project(format="tar.gz", filename=filename, upload=upload)

        self.project.deliver_file.assert_called_once_with(**expected_kwargs)

    @pytest.mark.parametrize(
        "format,filename,expected_kwargs",
        [
            (
                "json",
                "my-project.json",
                {
                    "content": b'{\n  "a": "b"\n}',
                    "filename": "my-project.json",
                    "upload": False,
                    "stdout": False,
                },
            ),
            (
                "toml",
                "my-project.toml",
                {
                    "content": b'a = "b"\n',
                    "filename": "my-project.toml",
                    "upload": False,
                    "stdout": False,
                },
            ),
            (
                "yaml",
                "my-project.toml",
                {
                    "content": b"a: b\n",
                    "filename": "my-project.toml",
                    "upload": False,
                    "stdout": False,
                },
            ),
            ("unknown", "unknown.txt", {}),
        ],
    )
    def test_export_project(self, format, filename, expected_kwargs):
        class MockResponse:
            content = b"binary-data"

        self.project.reptor.api.projects.project = MagicMock()
        self.project.reptor.api.projects.project.to_dict = MagicMock(
            return_value={"a": "b"}
        )
        self.project.reptor.api.projects.project.name = "my-project"
        self.project.deliver_file = MagicMock()
        self.project.reptor.api.projects.post = MagicMock(return_value=MockResponse())

        with pytest.raises(ValueError) if format == "unknown" else nullcontext():
            assert (
                self.project._export_project(format=format, filename=filename) is None
            )
        if format != "unknown":
            self.project.deliver_file.assert_called_once_with(**expected_kwargs)
        else:
            self.project.deliver_file.assert_not_called()

    def test_render_error(self):
        class MockResponse:
            content = {
                "pdf": None,
                "messages": [
                    {
                        "level": "error",
                        "message": "Template compilation error: Element is missing end tag.",
                        "details": "details",
                        "location": {
                            "type": "design",
                            "id": "5755c339-9ca7-4f83-a251-5490cfcf67e7",
                            "name": "Demo",
                            "path": None,
                        },
                    },
                    {"level": "warning", "message": "Template Warning"},
                ],
            }

            def json(self):
                return self.content

        self.project.reptor.api.projects.check_report = MagicMock(return_value={})
        exception = HTTPError("Raise for rendering error")
        exception.response = MockResponse()
        self.project.reptor.api.projects.post = Mock(
            side_effect=exception,
            return_value=MockResponse(),
        )
        self.project.reptor.api.projects.project = MagicMock()
        self.project.reptor.api.projects.project.name = "error-project"
        self.project.reptor.api.projects.log.error = MagicMock()
        self.project.reptor.api.projects.log.warning = MagicMock()

        # Assert rendering errors are logged
        with pytest.raises(HTTPError):
            self.project._render_project()
        self.project.reptor.api.projects.log.error.assert_called_once()
        self.project.reptor.api.projects.log.warning.assert_called_once()

        # Assert reraise if no json message
        exception.response.json = MagicMock(side_effect=NotImplementedError)
        with pytest.raises(HTTPError):
            self.project._render_project()

    def test_deliver_file(self):
        content = b"binary-data"
        filename = "test.tar.gz"
        default_filename = "my-project.tar.gz"
        sys.stdout.buffer.write = MagicMock()
        self.project.reptor.api.notes.upload_file = MagicMock()

        # Stdout, no upload
        self.project.deliver_file(
            content=content,
            filename=default_filename,
            upload=False,
            stdout=True,
        )
        sys.stdout.buffer.write.assert_called_once_with(content)
        self.project.reptor.api.notes.upload_file.assert_not_called()

        # Stdout, upload
        sys.stdout.buffer.write = MagicMock()
        self.project.deliver_file(
            content=content, filename=default_filename, upload=True, stdout=True
        )
        sys.stdout.buffer.write.assert_called_once_with(content)
        self.project.reptor.api.notes.upload_file.assert_not_called()
        # self.project.reptor.api.notes.upload_file.assert_called_once_with(
        #    content=content, filename=default_filename, notetitle="Uploads"
        # )

        # File, no upload
        m = mock_open()
        with patch("builtins.open", m, create=True):
            sys.stdout.buffer.write = MagicMock()
            self.project.reptor.api.notes.upload_file = MagicMock()
            self.project.deliver_file(
                content=content,
                filename=filename,
                upload=False,
                stdout=False,
            )
            sys.stdout.buffer.write.assert_not_called()
            self.project.reptor.api.notes.upload_file.assert_not_called()
            m.assert_called_once_with(filename, "wb")
            handle = m()
            handle.write.assert_called_once_with(content)

        # Write to file
        m = mock_open()
        with patch("builtins.open", m, create=True):
            sys.stdout.buffer.write = MagicMock()
            self.project.reptor.api.notes.upload_file = MagicMock()
            self.project.deliver_file(
                content=content,
                filename=filename,
                upload=False,
                stdout=False,
            )
            sys.stdout.buffer.write.assert_not_called()
            self.project.reptor.api.notes.upload_file.assert_not_called()
            m.assert_called_once_with(filename, "wb")
            handle = m()
            handle.write.assert_called_once_with(content)

        # File with default filename, upload
        m = mock_open()
        with patch("builtins.open", m, create=True):
            sys.stdout.buffer.write = MagicMock()
            self.project.reptor.api.notes.upload_file = MagicMock()
            self.project.deliver_file(
                content=content,
                filename=default_filename,
                upload=True,
                stdout=False,
            )
            sys.stdout.buffer.write.assert_not_called()
            self.project.reptor.api.notes.upload_file.assert_called_once_with(
                content=content, filename=default_filename, notetitle="Uploads"
            )
            m.assert_not_called()
