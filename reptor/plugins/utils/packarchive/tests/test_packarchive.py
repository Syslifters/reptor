import contextlib
import io
import json
import tarfile
import tempfile
import uuid
from pathlib import Path

import pytest
import tomli_w

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


class TestNormalizeNotes:
    def setup_method(self):
        self.packer = PackArchive(directories=[], output=io.BytesIO())

    def test_adds_null_parent_and_checked_to_notes(self):
        data = {"notes": [{"title": "Note 1"}]}
        self.packer.normalize_notes(data)
        assert data["notes"][0]["parent"] is None
        assert data["notes"][0]["checked"] is None

    def test_adds_null_parent_and_checked_to_default_notes(self):
        data = {"default_notes": [{"title": "Default"}]}
        self.packer.normalize_notes(data)
        assert data["default_notes"][0]["parent"] is None
        assert data["default_notes"][0]["checked"] is None

    def test_adds_null_parent_and_checked_to_project_type_default_notes(self):
        data = {
            "project_type": {
                "default_notes": [{"title": "Design note"}],
            },
        }
        self.packer.normalize_notes(data)
        note = data["project_type"]["default_notes"][0]
        assert note["parent"] is None
        assert note["checked"] is None

    def test_preserves_existing_parent_and_checked(self):
        parent_id = str(uuid.uuid4())
        data = {
            "notes": [
                {"title": "Child", "parent": parent_id, "checked": True},
                {"title": "Unchecked", "parent": None, "checked": False},
            ],
        }
        self.packer.normalize_notes(data)
        assert data["notes"][0]["parent"] == parent_id
        assert data["notes"][0]["checked"] is True
        assert data["notes"][1]["parent"] is None
        assert data["notes"][1]["checked"] is False

    def test_normalizes_all_note_collections(self):
        data = {
            "notes": [{"title": "Project note"}],
            "default_notes": [{"title": "Default note"}],
            "project_type": {
                "default_notes": [{"title": "Design note"}],
            },
        }
        self.packer.normalize_notes(data)
        for note in (
            data["notes"][0],
            data["default_notes"][0],
            data["project_type"]["default_notes"][0],
        ):
            assert note["parent"] is None
            assert note["checked"] is None

    def test_skips_non_list_note_collections(self):
        data = {
            "notes": {"title": "not a list"},
            "default_notes": "also not a list",
            "project_type": {"default_notes": None},
        }
        self.packer.normalize_notes(data)
        assert data["notes"] == {"title": "not a list"}
        assert data["default_notes"] == "also not a list"
        assert data["project_type"]["default_notes"] is None

    def test_skips_non_dict_note_items(self):
        data = {"notes": ["string note", 42, None, {"title": "Real note"}]}
        self.packer.normalize_notes(data)
        assert data["notes"][0] == "string note"
        assert data["notes"][1] == 42
        assert data["notes"][2] is None
        assert data["notes"][3]["parent"] is None
        assert data["notes"][3]["checked"] is None

    def test_noop_when_no_notes(self):
        data = {"format": "projects/v1", "id": str(uuid.uuid4())}
        self.packer.normalize_notes(data)
        assert data == {"format": "projects/v1", "id": data["id"]}

    def test_handles_missing_project_type(self):
        data = {"notes": [{"title": "Only notes"}]}
        self.packer.normalize_notes(data)
        assert data["notes"][0]["parent"] is None
        assert data["notes"][0]["checked"] is None

    def test_fills_only_missing_fields(self):
        data = {
            "notes": [
                {"title": "Has parent", "parent": "p1"},
                {"title": "Has checked", "checked": True},
            ],
        }
        self.packer.normalize_notes(data)
        assert data["notes"][0]["parent"] == "p1"
        assert data["notes"][0]["checked"] is None
        assert data["notes"][1]["parent"] is None
        assert data["notes"][1]["checked"] is True


class TestPackExport:
    def pack(self, files, format):
        with mock_files(
            files=files, format=format
        ) as d, tempfile.TemporaryFile() as output:
            PackArchive(directories=[d], output=output).run()
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
                        "format": "projecttypes/v1",
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
                        "format": "projecttypes/v1",
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
