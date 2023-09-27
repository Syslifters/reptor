import json
import os
import pathlib
import subprocess
import time

import pytest
import yaml

from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.api.NotesAPI import NotesAPI
from reptor.lib.reptor import Reptor


@pytest.fixture(scope="session")
def projects_api():
    reptor = Reptor()
    return ProjectsAPI(reptor=reptor)


@pytest.fixture(scope="session")
def notes_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"private_note": False}
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="module")
def uploads_id(notes_api):
    notes_api.write_note("Create Note")
    uploads_note = get_note("Uploads", None)
    assert uploads_note is not None
    return uploads_note["id"]


@pytest.fixture(autouse=True, scope="session")
def delete_notes(notes_api):
    yield

    # Delete all notes via notes_api
    for note in get_notes():
        notes_api.delete_note(note["id"])
    # Assert notes are gone
    notes = get_notes()
    assert len(notes) == 0


@pytest.fixture(autouse=True, scope="session")
def delete_findings(projects_api):
    # Delete findings via projects_api
    for finding in projects_api.get_findings():
        projects_api.delete_finding(finding.id)
    # Assert findings are gone
    findings = projects_api.get_findings()
    assert len(findings) == 0


def get_notes(private=False):
    cmd = ["reptor", "note", "--list", "--json"]
    if private:
        cmd.append("--private-note")

    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
    )
    notes, _ = p.communicate()
    notes = json.loads(notes.decode())
    p.wait()
    assert p.returncode == 0
    return notes


def get_note(name, parent, notes=None):
    if notes is None:
        notes = get_notes()
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


@pytest.mark.integration
@pytest.fixture(scope="session", autouse=True)
def setUp():
    # Get existing project id
    p = subprocess.Popen(
        ["reptor", "project", "--json"],
        stdout=subprocess.PIPE,
    )
    p.wait()
    projects, _ = p.communicate()
    projects = json.loads(projects.decode())
    assert p.returncode == 0
    project_id = projects[-1]["id"]

    # Rename config file
    filename_timestamp = int(time.time())
    try:
        os.rename(
            pathlib.Path.home() / ".sysreptor/config.yaml",
            pathlib.Path.home() / f".sysreptor/config.{filename_timestamp}.yaml",
        )
    except FileNotFoundError:
        pass

    # Test reptor conf and thereby setup config file
    p = subprocess.Popen(
        ["reptor", "conf"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
    )
    read_until(p.stdout)
    p.stdin.write(os.environ.get("SYSREPTOR_SERVER", "").encode("utf-8") + b"\n")
    p.stdin.flush()

    read_until(p.stdout)
    p.stdin.write(os.environ.get("SYSREPTOR_API_TOKEN", "").encode("utf-8") + b"\n")
    p.stdin.flush()

    read_until(p.stdout)
    p.stdin.write(project_id.encode("utf-8") + b"\n")
    p.stdin.flush()

    read_until(p.stdout)
    p.stdin.write(b"y\n")
    p.stdin.flush()
    p.wait(timeout=5)

    # Assert config file was created correctly
    with open(pathlib.Path.home() / ".sysreptor/config.yaml") as f:
        config = yaml.safe_load(f)
    assert config["server"] == os.environ.get("SYSREPTOR_SERVER", "")
    assert config["token"] == os.environ.get("SYSREPTOR_API_TOKEN", "")
    assert config["project_id"] == project_id

    yield

    # Remove integration test config file
    try:
        os.remove(pathlib.Path.home() / ".sysreptor/config.yaml")
    except FileNotFoundError:
        pass
    # Restore config file
    try:
        os.rename(
            pathlib.Path.home() / f".sysreptor/config.{filename_timestamp}.yaml",
            pathlib.Path.home() / ".sysreptor/config.yaml",
        )
    except FileNotFoundError:
        pass


def test_dummy():
    assert True
