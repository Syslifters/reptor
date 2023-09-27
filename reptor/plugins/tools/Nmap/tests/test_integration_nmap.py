import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api


@pytest.mark.integration
class TestIntegrationNmap(object):
    def test_nmap_single_note(self, notes_api):
        input_path = Path(os.path.dirname(__file__)) / "data/nmap_multi_target.xml"

        p = subprocess.Popen(
            ["reptor", "nmap", "-oX", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=input_path.read_bytes())
        p.wait()
        assert p.returncode == 0

        note = notes_api.get_note_by_title("nmap", parent_notename="Uploads")
        note_lines = note.text.splitlines()
        assert (
            "| www.google.com | 142.250.180.228 | 443/tcp | https | gws |" in note_lines
        )
        assert (
            "| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
            in note_lines
        )

    def test_nmap_multi_note(self, notes_api):
        nmap_output_path = (
            Path(os.path.dirname(__file__)) / "data/nmap_multi_target.xml"
        )

        p = subprocess.Popen(
            ["reptor", "nmap", "-oX", "--upload", "--multi-notes"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        p.communicate(input=nmap_output_path.read_bytes())
        p.wait()
        assert p.returncode == 0

        note = notes_api.get_note_by_title("142.250.180.228", parent_notename="nmap")
        note_lines = note.text.splitlines()
        assert (
            "| www.google.com | 142.250.180.228 | 443/tcp | https | gws |" in note_lines
        )
        assert (
            "| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
            not in note_lines
        )

        note = notes_api.get_note_by_title("34.249.200.254", parent_notename="nmap")
        note_lines = note.text.splitlines()
        assert (
            "| www.google.com | 142.250.180.228 | 443/tcp | https | gws |"
            not in note_lines
        )
        assert (
            "| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
            in note_lines
        )
