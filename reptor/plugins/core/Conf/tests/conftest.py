import json
import os
import pathlib
import subprocess
import time

import pytest
import yaml


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
