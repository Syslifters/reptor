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

    def test_fills_missing_parent_and_checked(self):
        parent_id = str(uuid.uuid4())
        data = {
            "notes": [
                {"title": "Missing both"},
                {"title": "Has parent", "parent": parent_id},
                {"title": "Has checked", "checked": True},
                {"title": "Child", "parent": parent_id, "checked": False},
                {"file": "notes.toml"},
                "skip-me",
            ],
            "default_notes": [{"title": "Default"}],
            "project_type": {"default_notes": [{"title": "Design"}]},
        }
        self.packer.normalize_notes(data)

        assert data["notes"][0]["parent"] is None and data["notes"][0]["checked"] is None
        assert data["notes"][1]["parent"] == parent_id and data["notes"][1]["checked"] is None
        assert data["notes"][2]["parent"] is None and data["notes"][2]["checked"] is True
        assert data["notes"][3]["parent"] == parent_id and data["notes"][3]["checked"] is False
        assert data["notes"][4] == {"file": "notes.toml"}
        assert data["notes"][5] == "skip-me"
        assert data["default_notes"][0]["parent"] is None
        assert data["project_type"]["default_notes"][0]["checked"] is None

    def test_skips_invalid_collections(self):
        data = {
            "notes": {"title": "not a list"},
            "default_notes": "also not a list",
            "project_type": {"default_notes": None},
        }
        self.packer.normalize_notes(data)
        assert data["notes"] == {"title": "not a list"}
        assert data["default_notes"] == "also not a list"
        assert data["project_type"]["default_notes"] is None


class TestResolveNoteIncludes:
    def setup_method(self):
        self.packer = PackArchive(directories=[], output=io.BytesIO())

    def test_reassign_toplevel_note_order(self):
        parent_id = str(uuid.uuid4())
        notes = [
            {"title": "A", "parent": None, "order": 99},
            {"title": "Child", "parent": parent_id, "order": 5},
            {"title": "B", "parent": None, "order": 1},
            {"title": "C", "parent": "", "order": 0},
        ]
        self.packer.reassign_toplevel_note_order(notes)
        assert [n["order"] for n in notes] == [1, 5, 2, 3]

    def test_resolve_mixes_files_and_inline(self):
        parent_id = str(uuid.uuid4())
        with mock_files(
            {
                "notes1.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [
                        {"id": parent_id, "title": "N1", "order": 10},
                        {"title": "N1 child", "parent": parent_id, "order": 1},
                        {"title": "N2", "order": 20},
                    ],
                },
                "notes2.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [{"title": "N3"}, {"title": "N4"}],
                },
            }
        ) as d:
            data = {
                "notes": [
                    {"file": "notes1.toml"},
                    {"file": "notes2.toml"},
                    {"title": "Inline"},
                ],
            }
            included = self.packer.resolve_note_includes(data, "notes", d)

        assert len(included) == 2
        titles = [n["title"] for n in data["notes"]]
        assert titles == ["N1", "N1 child", "N2", "N3", "N4", "Inline"]
        by_title = {n["title"]: n for n in data["notes"]}
        assert [by_title[t]["order"] for t in ("N1", "N2", "N3", "N4", "Inline")] == list(
            range(1, 6)
        )
        assert by_title["N1 child"]["parent"] == parent_id
        assert by_title["N1 child"]["order"] == 1

    def test_rejects_invalid_includes(self):
        with mock_files(
            {
                "bad.toml": {
                    "format": "projects/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [{"title": "Nope"}],
                },
            }
        ) as d:
            with pytest.raises(ValueError, match='format "notes/v1"'):
                self.packer.resolve_note_includes(
                    {"notes": [{"file": "bad.toml"}]}, "notes", d
                )
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Invalid reference"):
                self.packer.resolve_note_includes(
                    {"notes": [{"file": "missing.toml"}]}, "notes", Path(tmpdir)
                )

    def test_resolve_nested_includes(self):
        parent_id = str(uuid.uuid4())
        with mock_files(
            {
                "notes1.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [
                        {"file": "notes2.toml"},
                        {"title": "From1"},
                    ],
                },
                "notes2.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [
                        {"file": "notes3.toml"},
                        {"id": parent_id, "title": "From2", "order": 9},
                        {"title": "From2 child", "parent": parent_id, "order": 2},
                    ],
                },
                "notes3.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [{"title": "From3", "order": 5}],
                },
            }
        ) as d:
            data = {"notes": [{"file": "notes1.toml"}, {"title": "Inline"}]}
            included = self.packer.resolve_note_includes(data, "notes", d)

        assert len(included) == 3
        titles = [n["title"] for n in data["notes"]]
        assert titles == ["From3", "From2", "From2 child", "From1", "Inline"]
        by_title = {n["title"]: n for n in data["notes"]}
        assert [by_title[t]["order"] for t in ("From3", "From2", "From1", "Inline")] == [
            1, 2, 3, 4
        ]
        assert by_title["From2 child"]["parent"] == parent_id
        assert by_title["From2 child"]["order"] == 2

    def test_rejects_circular_includes(self):
        with mock_files(
            {
                "a.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [{"file": "b.toml"}],
                },
                "b.toml": {
                    "format": "notes/v1",
                    "id": str(uuid.uuid4()),
                    "notes": [{"file": "a.toml"}],
                },
            }
        ) as d:
            with pytest.raises(ValueError, match="Circular notes include"):
                self.packer.resolve_note_includes(
                    {"notes": [{"file": "a.toml"}]}, "notes", d
                )


class TestPackExport:
    def pack(self, files, format, entry=None):
        with mock_files(
            files=files, format=format
        ) as d, tempfile.TemporaryFile() as output:
            target = (d / entry) if entry else d
            PackArchive(directories=[target], output=output).run()
            output.flush()
            output.seek(0)
            return tarfile.open(fileobj=io.BytesIO(output.read()), mode="r:gz")

    def _read_packed_json(self, tar, resource_id):
        return json.loads(tar.extractfile(f"{resource_id}.json").read())

    @pytest.mark.parametrize("format", ["toml", "json"])
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

    @pytest.mark.parametrize("format", ["toml", "json"])
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

    @pytest.mark.parametrize("format", ["toml", "json"])
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

    def test_pack_project_notes_includes_order_and_sidecars(self):
        project_id, design_id = str(uuid.uuid4()), str(uuid.uuid4())
        notes1_id, notes2_id, parent_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        tar = self.pack(
            files={
                "project1.toml": {
                    "id": project_id,
                    "format": "projects/v1",
                    "project_type": {
                        "id": design_id,
                        "format": "projecttypes/v1",
                    },
                    "notes": [
                        {"file": "notes1.toml"},
                        {"file": "notes2.toml"},
                        {"title": "Inline1"},
                        {"title": "Inline2"},
                    ],
                },
                "notes1.toml": {
                    "format": "notes/v1",
                    "id": notes1_id,
                    "notes": [
                        {"id": parent_id, "title": "A1", "order": 50},
                        {"title": "A1 child", "parent": parent_id, "order": 3},
                        {"title": "A2", "order": 60},
                        {"title": "A3", "order": 70},
                    ],
                },
                "notes2.toml": {
                    "format": "notes/v1",
                    "id": notes2_id,
                    "notes": [{"title": "B1"}, {"title": "B2"}],
                },
                "notes1-images/note_img.png": create_png_file(),
                "notes1-files/note_file.txt": b"from notes",
                "project1-images/project_img.png": create_png_file(),
            },
            format="toml",
            entry="project1.toml",
        )
        names = set(tar.getnames())
        assert f"{project_id}-images/note_img.png" in names
        assert f"{project_id}-files/note_file.txt" in names
        assert f"{project_id}-images/project_img.png" in names
        assert not any(n.startswith(f"{notes1_id}-") for n in names)

        data = self._read_packed_json(tar, project_id)
        titles = [n["title"] for n in data["notes"]]
        assert titles == ["A1", "A1 child", "A2", "A3", "B1", "B2", "Inline1", "Inline2"]
        by_title = {n["title"]: n for n in data["notes"]}
        assert [by_title[t]["order"] for t in (
            "A1", "A2", "A3", "B1", "B2", "Inline1", "Inline2"
        )] == list(range(1, 8))
        assert by_title["A1 child"]["parent"] == parent_id
        assert by_title["A1 child"]["order"] == 3
        assert {f["name"] for f in data["images"]} >= {"note_img.png", "project_img.png"}
        assert "note_file.txt" in {f["name"] for f in data["files"]}

    def test_pack_nested_notes_includes_and_sidecars(self):
        project_id, design_id = str(uuid.uuid4()), str(uuid.uuid4())
        notes1_id, notes2_id, notes3_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        tar = self.pack(
            files={
                "project1.toml": {
                    "id": project_id,
                    "format": "projects/v1",
                    "project_type": {
                        "id": design_id,
                        "format": "projecttypes/v1",
                    },
                    "notes": [{"file": "notes1.toml"}, {"title": "Inline"}],
                },
                "notes1.toml": {
                    "format": "notes/v1",
                    "id": notes1_id,
                    "notes": [{"file": "notes2.toml"}, {"title": "From1"}],
                },
                "notes2.toml": {
                    "format": "notes/v1",
                    "id": notes2_id,
                    "notes": [{"file": "notes3.toml"}, {"title": "From2"}],
                },
                "notes3.toml": {
                    "format": "notes/v1",
                    "id": notes3_id,
                    "notes": [{"title": "From3"}],
                },
                "notes3-images/nested_img.png": create_png_file(),
                "notes3-files/nested_file.txt": b"nested",
            },
            format="toml",
            entry="project1.toml",
        )
        names = set(tar.getnames())
        assert f"{project_id}-images/nested_img.png" in names
        assert f"{project_id}-files/nested_file.txt" in names
        assert not any(n.startswith(f"{notes3_id}-") for n in names)

        data = self._read_packed_json(tar, project_id)
        assert [n["title"] for n in data["notes"]] == [
            "From3", "From2", "From1", "Inline"
        ]
        assert [n["order"] for n in data["notes"]] == [1, 2, 3, 4]
        assert "nested_img.png" in {f["name"] for f in data["images"]}
        assert "nested_file.txt" in {f["name"] for f in data["files"]}

    def test_pack_project_type_default_notes_includes(self):
        project_id, design_id, notes_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        tar = self.pack(
            files={
                "project1.toml": {
                    "id": project_id,
                    "format": "projects/v1",
                    "project_type": {"file": "design.toml"},
                },
                "design.toml": {
                    "id": design_id,
                    "format": "projecttypes/v1",
                    "default_notes": [
                        {"file": "defaults.toml"},
                        {"title": "Inline default"},
                    ],
                },
                "defaults.toml": {
                    "format": "notes/v1",
                    "id": notes_id,
                    "notes": [
                        {"title": "Default A", "order": 9},
                        {"title": "Default B", "order": 8},
                    ],
                },
                "defaults-images/default_img.png": create_png_file(),
                "defaults-files/default_file.txt": b"asset from notes",
                "design-assets/logo.png": create_png_file(),
            },
            format="toml",
            entry="project1.toml",
        )
        names = set(tar.getnames())
        assert {f"{design_id}-assets/{n}" for n in (
            "default_img.png", "default_file.txt", "logo.png"
        )} <= names
        assert not any(n.startswith(f"{notes_id}-") for n in names)

        data = self._read_packed_json(tar, project_id)
        default_notes = data["project_type"]["default_notes"]
        assert [n["title"] for n in default_notes] == [
            "Default A", "Default B", "Inline default"
        ]
        assert [n["order"] for n in default_notes] == [1, 2, 3]
        assert {f["name"] for f in data["project_type"]["assets"]} >= {
            "default_img.png", "default_file.txt", "logo.png"
        }

    def test_pack_inline_project_type_default_notes_includes(self):
        project_id, design_id, notes_id = (
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        )
        tar = self.pack(
            files={
                "project1.toml": {
                    "id": project_id,
                    "format": "projects/v1",
                    "project_type": {
                        "id": design_id,
                        "format": "projecttypes/v1",
                        "default_notes": [{"file": "defaults.toml"}],
                    },
                },
                "defaults.toml": {
                    "format": "notes/v1",
                    "id": notes_id,
                    "notes": [{"title": "From file"}],
                },
            },
            format="toml",
            entry="project1.toml",
        )
        data = self._read_packed_json(tar, project_id)
        notes = data["project_type"]["default_notes"]
        assert [n["title"] for n in notes] == ["From file"]
        assert notes[0]["order"] == 1
