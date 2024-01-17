import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import tomli


@pytest.mark.integration
class TestUnPackArchive(object):
    input_path = Path(os.path.dirname(__file__)) / "data/unpacked"
    archive_path = Path(os.path.dirname(__file__)) / "data/packed_archive.tar.gz"
    unpacked_path = Path(os.path.dirname(__file__)) / "data/unpacked_archive"

    @pytest.fixture(autouse=True)
    def tearDown(self):
        yield
        # Delete output files, ignore errors
        for path in [self.archive_path, self.unpacked_path]:
            try:
                if os.path.isfile(path):
                    path.unlink()
                else:
                    shutil.rmtree(path)
            except FileNotFoundError:
                pass

    @pytest.mark.parametrize("format", ["toml"])
    def test_pack_unpack(self, format):
        # Pack archive
        p = subprocess.Popen(
            [
                "reptor",
                "packarchive",
                "--output",
                str(self.archive_path),
                str(self.input_path),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate()
        assert p.returncode == 0

        # Unpack archive
        p = subprocess.Popen(
            [
                "reptor",
                "unpackarchive",
                "--format",
                format,
                "--output",
                str(self.unpacked_path),
                str(self.archive_path),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate()
        assert p.returncode == 0

        # Compare unpacked files
        assert set(os.listdir(self.input_path)) == set(os.listdir(self.unpacked_path))
        original = tomli.loads((self.input_path / "project.toml").read_text())
        if format == "json":
            unpacked = json.loads((self.unpacked_path / "project.json").read_text())
        elif format == "toml":
            unpacked = tomli.loads((self.unpacked_path / "project.toml").read_text())
        else:
            raise ValueError(f"Unknown format: {format}")
        assert unpacked == original
