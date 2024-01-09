import io
import json
import tarfile
import tomli_w
import contextlib
import tempfile
import pytest
import uuid
from tarfile import TarFile
from pathlib import Path

from reptor.lib.reptor import Reptor
from reptor.plugins.utils.packarchive.packarchive import PackArchive


@contextlib.contextmanager
def mock_files(files, format="toml"):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        for filename, content in files.items():
            filename = tmpdir / Path(filename)
            if isinstance(content, dict) and not filename.suffix:
                filename = filename.with_suffix(f".{format}")
            filename.parent.mkdir(parents=True, exist_ok=True)

            if isinstance(content, bytes):
                filename.write_bytes(content)
            elif isinstance(content, str):
                filename.write_text(content)
            elif isinstance(content, dict) and format == "json":
                filename.write_text(json.dumps(content))
            elif isinstance(content, dict) and format == "toml":
                filename.write_text(tomli_w.dumps(content))
            else:
                raise Exception(f"Unhandled type: {type(content)}")

        yield tmpdir


def create_png_file() -> bytes:
    # 1x1 pixel PNG file
    # Source: https://commons.wikimedia.org/wiki/File:1x1.png
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\r"
        + b"IHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03"
        + b"PLTE\x00\x00\x00\xa7z=\xda\x00\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x00\n"
        + b"IDAT\x08\xd7c`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class TestPackExport:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()

    def pack(self, files, format):
        with mock_files(
            files=files, format=format
        ) as d, tempfile.TemporaryFile() as output:
            PackArchive(reptor=self.reptor, directories=[d], output=output).run()
            output.flush()
            output.seek(0)
            return tarfile.open(fileobj=io.BytesIO(output.read()), mode="r:gz")

    @pytest.mark.parametrize(
        ["format"],
        [
            ("toml",),
            ("json",),
        ],
    )
    def test_pack_project_name(self, format):
        project_id = str(uuid.uuid4())
        design_id = str(uuid.uuid4())
        tar = self.pack(
            files={
                f"project1.{format}": {
                    "id": project_id,
                    "format": "projects/v1",
                    "project_type": {
                        "id": design_id,
                    },
                },
                "project1-images/img1.png": create_png_file(),
                "project1-files/file1.txt": b"test",
                "project1-assets/file2.txt": b"test",
            },
            format=format,
        )
        assert set(tar.getnames()) == {
            f"{project_id}.json",
            f"{project_id}-images",
            f"{project_id}-images/img1.png",
            f"{project_id}-files",
            f"{project_id}-files/file1.txt",
            f"{design_id}-assets",
            f"{design_id}-assets/file2.txt",
        }

    @pytest.mark.parametrize(
        ["format"],
        [
            ("toml",),
            ("json",),
        ],
    )
    def test_pack_project_id(self, format):
        project_id = str(uuid.uuid4())
        design_id = str(uuid.uuid4())
        tar = self.pack(
            files={
                f"{project_id}.{format}": {
                    "id": project_id,
                    "format": "projects/v1",
                    "project_type": {
                        "id": design_id,
                        "format": "projecttype/v1",
                    },
                },
                f"{project_id}-images/img1.png": create_png_file(),
                f"{project_id}-files/file1.txt": b"test",
                f"{design_id}-assets/file2.txt": b"test",
            },
            format=format,
        )
        assert set(tar.getnames()) == {
            f"{project_id}.json",
            f"{project_id}-images",
            f"{project_id}-images/img1.png",
            f"{project_id}-files",
            f"{project_id}-files/file1.txt",
            f"{design_id}-assets",
            f"{design_id}-assets/file2.txt",
        }

    @pytest.mark.parametrize(
        ["format"],
        [
            ("toml",),
            ("json",),
        ],
    )
    def test_pack_template_name(self, format):
        template_id = str(uuid.uuid4())
        tar = self.pack(
            files={
                f"template1.{format}": {
                    "id": template_id,
                    "format": "templates/v1",
                },
                "template1-images/img1.png": create_png_file(),
            },
            format=format,
        )
        assert set(tar.getnames()) == {
            f"{template_id}.json",
            f"{template_id}-images",
            f"{template_id}-images/img1.png",
        }
