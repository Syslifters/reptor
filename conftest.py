import os
import pathlib
import time

import pytest
import requests

from reptor.api.NotesAPI import NotesAPI
from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.api.TemplatesAPI import TemplatesAPI
from reptor.lib.reptor import Reptor
from test_helpers import conf, get_note, get_notes


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
    project_designs = ProjectDesignsAPI(reptor=reptor).search()
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
    reptor._config._raw_config["cli"] = {"personal_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="session")
def personal_notes_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"personal_note": True}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="session")
def project_design_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"personal_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return ProjectDesignsAPI(reptor=reptor)


@pytest.fixture(scope="session")
def templates_api():
    reptor = Reptor()
    reptor._config._raw_config["cli"] = {"personal_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return TemplatesAPI(reptor=reptor)


@pytest.fixture(scope="module")
def uploads_id(notes_api):
    notes_api.write_note(title="Create Note")
    uploads_note = get_note("Uploads", None)
    assert uploads_note is not None
    return uploads_note["id"]


@pytest.fixture(scope="module")
def personal_uploads_id(personal_notes_api):
    personal_notes_api.write_note(title="Create Note")
    uploads_note = get_note("Uploads", None, private=True)
    assert uploads_note is not None
    return uploads_note["id"]


@pytest.fixture(autouse=True, scope="session")
def delete_notes(setUp, notes_api):
    yield

    # Delete all notes via notes_api
    for note in get_notes():
        try:
            notes_api.delete_note(note["id"])
        except requests.exceptions.HTTPError:
            pass
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



