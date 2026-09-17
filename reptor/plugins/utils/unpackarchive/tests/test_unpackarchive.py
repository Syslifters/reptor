import io
import json
import tarfile

import pytest
import tomli
import tomlkit

from reptor.plugins.utils.unpackarchive.unpackarchive import (
    UnpackArchive,
    format_notes,
    order_notes_tree,
    to_toml,
)
from reptor.utils import file_operations


def build_archive(member_name: str, payload: bytes) -> io.BytesIO:
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as tar:
        info = tarfile.TarInfo(name=member_name)
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    archive.seek(0)
    return archive


def test_to_toml_preserves_leading_backslash_newline():
    data = {
        "report": {
            "scope": "\\\n\\\\\nThe scope of this pentest included:\n* item\n\\\\\n\\\n",
            "attack_paths_description": "\\\n\\\\\nasdasd\\\\\n\\\n",
        }
    }
    assert tomli.loads(tomlkit.dumps(to_toml(data))) == data


def test_safe_extractall_rejects_path_traversal(tmp_path):
    helper = getattr(file_operations, "safe_extractall", None)
    assert helper is not None

    destination = tmp_path / "extract"
    destination.mkdir()
    with tarfile.open(fileobj=build_archive("../escape.txt", b"x"), mode="r:gz") as tar:
        with pytest.raises(tarfile.TarError):
            helper(tar, destination)
    assert not (tmp_path / "escape.txt").exists()


def test_safe_extractall_allows_valid_archive(tmp_path):
    helper = getattr(file_operations, "safe_extractall", None)
    assert helper is not None

    payload = json.dumps({"title": "project"}).encode()
    destination = tmp_path / "extract"
    destination.mkdir()
    with tarfile.open(fileobj=build_archive("project.json", payload), mode="r:gz") as tar:
        helper(tar, destination)
    assert (destination / "project.json").read_text() == payload.decode()


def test_unpackarchive_rejects_malicious_archive(tmp_path):
    archive_path = tmp_path / "archive.tar.gz"
    archive_path.write_bytes(build_archive("../escape.json", b'{"title": "bad"}').getvalue())
    with archive_path.open("rb") as archive_file:
        with pytest.raises(tarfile.TarError):
            UnpackArchive(
                files=[archive_file], output=str(tmp_path / "output"), format="json"
            ).run()
    assert not (tmp_path / "escape.json").exists()


def test_order_notes_tree():
    notes = [
        {"id": "child-b2", "parent": "root-b", "order": 2},
        {"id": "root-b", "parent": None, "order": 2},
        {"id": "child-a1", "parent": "root-a", "order": 1},
        {"id": "root-a", "parent": None, "order": 1},
        {"id": "child-b1", "parent": "root-b", "order": 1},
        {"id": "child-a2", "parent": "root-a", "order": 2},
        {"id": "orphan", "parent": "missing", "order": 1},
    ]
    assert [n["id"] for n in order_notes_tree(notes)] == [
        "root-a", "child-a1", "child-a2", "root-b", "child-b1", "child-b2", "orphan"
    ]


def test_to_toml_note_field_order():
    note = {
        "text": "body",
        "excalidraw_data": "{}",
        "checked": True,
        "icon_emoji": "📝",
        "assignee": "user-1",
        "updated": "2024-01-02",
        "created": "2024-01-01",
        "order": 3,
        "parent": "p1",
        "type": "note",
        "id": "n1",
        "title": "Note",
        "extra": "keep",
    }
    keys = list(tomli.loads(tomlkit.dumps(to_toml(note, is_note=True))).keys())
    assert keys == [
        "title",
        "id",
        "type",
        "parent",
        "order",
        "created",
        "updated",
        "assignee",
        "checked",
        "icon_emoji",
        "text",
        "excalidraw_data",
        "extra",
    ]

    data = {"format": "notes/v1", "notes": [{"text": "body", "order": 1, "id": "n1", "title": "Note"}]}
    assert list(tomli.loads(tomlkit.dumps(to_toml(data)))["notes"][0].keys()) == [
        "title", "id", "order", "text"
    ]


def test_format_notes_targets():
    shuffled = lambda a, b: [
        {"id": b, "parent": None, "order": 2},
        {"id": a, "parent": None, "order": 1},
    ]

    notes_doc = {"format": "notes/v1", "notes": shuffled("a", "b")}
    format_notes(notes_doc)
    assert [n["id"] for n in notes_doc["notes"]] == ["a", "b"]

    project = {
        "format": "projects/v1",
        "notes": shuffled("n1", "n2"),
        "project_type": {"default_notes": shuffled("d1", "d2")},
    }
    format_notes(project)
    assert [n["id"] for n in project["notes"]] == ["n1", "n2"]
    assert [n["id"] for n in project["project_type"]["default_notes"]] == ["d1", "d2"]

    design = {"format": "projecttypes/v1", "default_notes": shuffled("d1", "d2")}
    format_notes(design)
    assert [n["id"] for n in design["default_notes"]] == ["d1", "d2"]

    template = {"format": "templates/v1", "notes": shuffled("a", "b")}
    format_notes(template)
    assert [n["id"] for n in template["notes"]] == ["b", "a"]


def test_unpackarchive_formats_notes_in_toml(tmp_path):
    payload = {
        "format": "notes/v1",
        "id": "notes-doc",
        "notes": [
            {"id": "child", "title": "Child", "parent": "root", "order": 1, "text": "c"},
            {"id": "root", "title": "Root", "parent": None, "order": 1, "text": "r"},
        ],
    }
    archive_path = tmp_path / "archive.tar.gz"
    archive_path.write_bytes(
        build_archive("notes-doc.json", json.dumps(payload).encode()).getvalue()
    )
    with archive_path.open("rb") as archive_file:
        UnpackArchive(
            files=[archive_file], output=str(tmp_path / "output"), format="toml"
        ).run()

    unpacked = tomli.loads((tmp_path / "output" / "notes-doc.toml").read_text())
    assert [n["id"] for n in unpacked["notes"]] == ["root", "child"]
    assert list(unpacked["notes"][0].keys()) == ["title", "id", "order", "text"]
