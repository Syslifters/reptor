import io
import json
import tarfile

import pytest
import tomli
import tomlkit

from reptor.plugins.utils.unpackarchive.unpackarchive import UnpackArchive, to_toml
from reptor.utils import file_operations


def test_to_toml_preserves_leading_backslash_newline():
    data = {
        "report": {
            "scope": "\\\n\\\\\nThe scope of this pentest included:\n* item\n\\\\\n\\\n",
            "attack_paths_description": "\\\n\\\\\nasdasd\\\\\n\\\n",
        }
    }
    unpacked = tomli.loads(tomlkit.dumps(to_toml(data)))
    assert unpacked == data


def build_archive(member_name: str, payload: bytes) -> io.BytesIO:
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as tar:
        info = tarfile.TarInfo(name=member_name)
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    archive.seek(0)
    return archive


def test_safe_extractall_rejects_path_traversal(tmp_path):
    helper = getattr(file_operations, "safe_extractall", None)
    assert helper is not None

    archive = build_archive("../escape.txt", b"path_traversal")
    destination = tmp_path / "extract"
    destination.mkdir()

    with tarfile.open(fileobj=archive, mode="r:gz") as tar:
        with pytest.raises(tarfile.TarError):
            helper(tar, destination)

    assert not (tmp_path / "escape.txt").exists()


def test_safe_extractall_allows_valid_archive(tmp_path):
    helper = getattr(file_operations, "safe_extractall", None)
    assert helper is not None

    payload = json.dumps({"title": "project"}).encode()
    archive = build_archive("project.json", payload)
    destination = tmp_path / "extract"
    destination.mkdir()

    with tarfile.open(fileobj=archive, mode="r:gz") as tar:
        helper(tar, destination)

    assert (destination / "project.json").read_text() == payload.decode()


def test_unpackarchive_rejects_malicious_archive(tmp_path):
    archive_path = tmp_path / "archive.tar.gz"
    archive_path.write_bytes(build_archive("../escape.json", b'{"title": "bad"}').getvalue())

    output_dir = tmp_path / "output"
    with archive_path.open("rb") as archive_file:
        unpacker = UnpackArchive(files=[archive_file], output=str(output_dir), format="json")
        with pytest.raises(tarfile.TarError):
            unpacker.run()

    assert not (tmp_path / "escape.json").exists()
