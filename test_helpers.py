"""Helper functions for integration tests."""
import json
import os
import pathlib
import subprocess

import yaml


def get_notes(private=False):
    cmd = ["reptor", "note", "--list", "--json"]
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        cmd.append("--insecure")
    if private:
        cmd.append("--private-note")

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
    )
    notes, _ = p.communicate()
    notes = json.loads(notes.decode())
    assert p.returncode == 0
    return notes


def get_note(name, parent, notes=None, private=False):
    if notes is None:
        notes = get_notes(private=private)
    if parent:
        pass
    for note in notes:
        if note["title"] == name and note["parent"] == parent:
            return note


def read_until(f, eof=": "):
    content = ""
    while char := f.read(1).decode():
        content += char
        if content.endswith(eof):
            break
    return content


def conf(project_id=""):
    # Test reptor conf and thereby setup config file
    p = subprocess.Popen(
        ["reptor", "conf"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
    )
    read_until(p.stdout)
    p.stdin.write(os.environ.get("SYSREPTOR_SERVER", "").encode("utf-8") + b"\n")  # type: ignore
    p.stdin.flush()  # type: ignore

    read_until(p.stdout)
    p.stdin.write(os.environ.get("SYSREPTOR_API_TOKEN", "").encode("utf-8") + b"\n")  # type: ignore
    p.stdin.flush()  # type: ignore

    read_until(p.stdout)
    p.stdin.write(project_id.encode("utf-8") + b"\n")  # type: ignore
    p.stdin.flush()  # type: ignore

    read_until(p.stdout)
    p.stdin.write(b"y\n")  # type: ignore
    p.stdin.flush()  # type: ignore
    p.wait(timeout=5)

    # Assert config file was created correctly
    with open(pathlib.Path.home() / ".sysreptor/config.yaml") as f:
        config = yaml.safe_load(f)
    assert config["server"] == os.environ.get("SYSREPTOR_SERVER", "")
    assert config["token"] == os.environ.get("SYSREPTOR_API_TOKEN", "")
    if project_id:
        assert config["project_id"] == project_id
    else:
        assert config["project_id"] is None
