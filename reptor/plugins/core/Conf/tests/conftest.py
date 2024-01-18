import json
import os
import pathlib
import subprocess
import time

import pytest
import yaml

from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.api.NotesAPI import NotesAPI
from reptor.lib.reptor import Reptor


@pytest.mark.integration
@pytest.fixture(scope="session", autouse=True)
def setUp():
    # Rename config file
    filename_timestamp = int(time.time())
    try:
        os.rename(
            pathlib.Path.home() / ".sysreptor/config.yaml",
            pathlib.Path.home() / f".sysreptor/config.{filename_timestamp}.yaml",
        )
    except FileNotFoundError:
        pass

    # Set API Token and URL
    conf()

    # Get design ID
    reptor = Reptor()
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["insecure"] = True
        reptor._config._raw_config["cli"] = {"insecure": True}
    project_designs = ProjectDesignsAPI(reptor=reptor).get_project_designs()
    for design in project_designs:
        if "Demo Calzone" in design.name:
            project_design_id = design.id
            break
    else:
        raise ValueError("Demo Calzone project design not found")

    # Create project
    projects_api = ProjectsAPI(reptor=reptor)
    project = projects_api.create_project(
        "Integration Test Project", project_design_id, tags=["integration-test"]
    )

    # Also add project_id
    conf(project_id=project.id)

    yield

    # Delete Project
    conf(project_id=project.id)
    reptor = Reptor()
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["insecure"] = True
        reptor._config._raw_config["cli"] = {"insecure": True}
    projects_api = ProjectsAPI(reptor=reptor)
    projects_api.delete_project()

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


@pytest.fixture(scope="session")
def projects_api():
    reptor = Reptor()
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["insecure"] = True
    return ProjectsAPI(reptor=reptor)


@pytest.fixture(scope="session")
def notes_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"private_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="session")
def private_notes_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"private_note": True}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="session")
def project_design_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"private_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return ProjectDesignsAPI(reptor=reptor)


@pytest.fixture(scope="module")
def uploads_id(notes_api):
    notes_api.write_note("Create Note")
    uploads_note = get_note("Uploads", None)
    assert uploads_note is not None
    return uploads_note["id"]


@pytest.fixture(scope="module")
def private_uploads_id(private_notes_api):
    private_notes_api.write_note("Create Note")
    uploads_note = get_note("Uploads", None, private=True)
    assert uploads_note is not None
    return uploads_note["id"]


@pytest.fixture(autouse=True, scope="session")
def delete_notes(setUp, notes_api):
    yield

    # Delete all notes via notes_api
    for note in get_notes():
        notes_api.delete_note(note["id"])
    # Assert notes are gone
    notes = get_notes()
    assert len(notes) == 0


@pytest.fixture(autouse=True, scope="session")
def delete_findings(setUp, projects_api):
    yield

    # Delete findings via projects_api
    for finding in projects_api.get_findings():
        projects_api.delete_finding(finding.id)
    # Assert findings are gone
    findings = projects_api.get_findings()
    assert len(findings) == 0


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
