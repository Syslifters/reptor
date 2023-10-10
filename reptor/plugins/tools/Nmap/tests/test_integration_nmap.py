import os
import subprocess
from pathlib import Path

import pytest

from reptor.plugins.core.Conf.tests.conftest import notes_api


@pytest.mark.integration
class TestIntegrationNmap(object):
    def test_nmap_note(self, notes_api):
        nmap_output_path = (
            Path(os.path.dirname(__file__)) / "data/nmap_multi_target.xml"
        )

        p = subprocess.Popen(
            ["reptor", "nmap", "-oX", "--upload"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate(input=nmap_output_path.read_bytes())
        assert p.returncode == 0

        nmap_note = notes_api.get_note_by_title("Nmap", parent_notetitle=None)
        note_lines = nmap_note.text.splitlines()
        assert (
            "| www.google.com | 142.250.180.228 | 443/tcp | https | gws |" in note_lines
        )
        assert (
            "| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
            in note_lines
        )

        ip_note = notes_api.get_note_by_title(
            "142.250.180.228", parent_notetitle="Nmap"
        )
        note_lines = ip_note.text.splitlines()
        assert (
            "| www.google.com | 142.250.180.228 | 443/tcp | https | gws |" in note_lines
        )
        assert (
            "| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
            not in note_lines
        )

        ip_note = notes_api.get_note_by_title("34.249.200.254", parent_notetitle="Nmap")
        note_lines = ip_note.text.splitlines()
        assert (
            "| www.google.com | 142.250.180.228 | 443/tcp | https | gws |"
            not in note_lines
        )
        assert (
            "| www.syslifters.com | 34.249.200.254 | 443/tcp | https | n/a |"
            in note_lines
        )
