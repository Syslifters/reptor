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
from test_fixtures.designs import (
    create_integration_designs,
    delete_integration_designs,
    seed_integration_report_content,
)
from test_helpers import conf, get_note, get_notes


def _expression_selects_integration(expr: str) -> bool:
    if not expr:
        return False
    return "integration" in expr and "not integration" not in expr


def pytest_configure(config):
    """Check if running integration tests via -k or -m."""
    k_filter = config.getoption("-k", default="") or ""
    m_filter = config.getoption("-m", default="") or ""
    config.run_integration_tests = _expression_selects_integration(
        k_filter
    ) or _expression_selects_integration(m_filter)


def skip_if_not_integration(request):
    """Skip fixture if not running integration tests"""
    if not getattr(request.config, "run_integration_tests", False):
        pytest.skip("Not running integration tests")


def _make_reptor(project_id=None):
    reptor = Reptor(
        server=os.environ.get("SYSREPTOR_SERVER"),
        token=os.environ.get("SYSREPTOR_API_TOKEN"),
        project_id=project_id or os.environ.get("SYSREPTOR_PROJECT_ID"),
    )
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["insecure"] = True
        reptor._config._raw_config["cli"] = {"insecure": True}
    return reptor


@pytest.fixture(scope="session", autouse=True)
def integration_setup(request):
    """Setup and teardown for integration tests"""
    if not getattr(request.config, "run_integration_tests", False):
        yield
        return

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

    reptor = _make_reptor()
    design_api = ProjectDesignsAPI(reptor=reptor)
    projects_api = ProjectsAPI(reptor=reptor)

    primary_design_id = None
    alt_design_id = None
    project = None

    try:
        primary_design_id, alt_design_id = create_integration_designs(design_api)
        os.environ["SYSREPTOR_ALT_DESIGN_ID"] = alt_design_id

        project = projects_api.create_project(
            f"Integration Test Project {primary_design_id[:8]}",
            primary_design_id,
            tags=["integration-test"],
        )
        os.environ["SYSREPTOR_PROJECT_ID"] = project.id
        conf(project_id=project.id)

        projects_api.init_project(project.id)
        # Re-bind design API context to the project's design for section seeding
        reptor = _make_reptor(project_id=project.id)
        projects_api = ProjectsAPI(reptor=reptor)
        seed_integration_report_content(projects_api)

        yield
    finally:
        # Delete project first (holds design references), then designs
        try:
            project_id = os.environ.get("SYSREPTOR_PROJECT_ID") or (
                project.id if project is not None else None
            )
            if project_id:
                try:
                    conf(project_id=project_id)
                    teardown_reptor = _make_reptor(project_id=project_id)
                    ProjectsAPI(reptor=teardown_reptor).delete_project()
                except requests.exceptions.HTTPError as exc:
                    if exc.response is None or exc.response.status_code != 404:
                        raise
        finally:
            teardown_reptor = _make_reptor()
            delete_integration_designs(
                ProjectDesignsAPI(reptor=teardown_reptor),
                primary_design_id,
                alt_design_id,
            )
            os.environ.pop("SYSREPTOR_ALT_DESIGN_ID", None)
            os.environ.pop("SYSREPTOR_PROJECT_ID", None)

            # Remove integration test config file
            try:
                os.remove(pathlib.Path.home() / ".sysreptor/config.yaml")
            except FileNotFoundError:
                pass
            # Restore config file
            try:
                os.rename(
                    pathlib.Path.home()
                    / f".sysreptor/config.{filename_timestamp}.yaml",
                    pathlib.Path.home() / ".sysreptor/config.yaml",
                )
            except FileNotFoundError:
                pass


@pytest.fixture(scope="session")
def projects_api(request):
    skip_if_not_integration(request)
    reptor = _make_reptor()
    return ProjectsAPI(reptor=reptor)


@pytest.fixture(scope="session")
def notes_api(request):
    skip_if_not_integration(request)
    reptor = _make_reptor()
    reptor._config._raw_config["cli"] = {"personal_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="session")
def personal_notes_api(request):
    skip_if_not_integration(request)
    reptor = _make_reptor()
    reptor._config._raw_config["cli"] = {"personal_note": True}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return NotesAPI(reptor=reptor)


@pytest.fixture(scope="session")
def project_design_api(request):
    skip_if_not_integration(request)
    reptor = _make_reptor()
    reptor._config._raw_config["cli"] = {"personal_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    return ProjectDesignsAPI(reptor=reptor)


@pytest.fixture(scope="session")
def alt_design_id(request, integration_setup):
    """Alternate design ID provisioned for render --design tests."""
    skip_if_not_integration(request)
    design_id = os.environ.get("SYSREPTOR_ALT_DESIGN_ID")
    if not design_id:
        pytest.fail("SYSREPTOR_ALT_DESIGN_ID not set by integration_setup")
    return design_id


@pytest.fixture(scope="session")
def templates_api(request):
    skip_if_not_integration(request)
    reptor = _make_reptor()
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
def delete_notes(request, integration_setup):
    """Cleanup notes after integration tests"""
    if not getattr(request.config, "run_integration_tests", False):
        yield
        return

    # Create notes_api only for integration tests
    reptor = _make_reptor()
    reptor._config._raw_config["cli"] = {"personal_note": False}
    if os.environ.get("HTTPS_PROXY", "").startswith("http://"):
        reptor._config._raw_config["cli"]["insecure"] = True
    notes_api = NotesAPI(reptor=reptor)

    yield

    # Delete all notes
    for note in get_notes():
        try:
            notes_api.delete_note(note["id"])
        except requests.exceptions.HTTPError:
            pass
    assert len(get_notes()) == 0


@pytest.fixture(autouse=True, scope="session")
def delete_findings(request, integration_setup):
    """Cleanup findings after integration tests"""
    if not getattr(request.config, "run_integration_tests", False):
        yield
        return

    # Create projects_api only for integration tests
    reptor = _make_reptor()
    projects_api = ProjectsAPI(reptor=reptor)

    yield

    # Delete all findings
    for finding in projects_api.get_findings():
        projects_api.delete_finding(finding.id)
    assert len(projects_api.get_findings()) == 0
