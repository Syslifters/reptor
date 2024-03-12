import json
import subprocess

import pytest


@pytest.mark.integration
class TestIntegrationDeleteFinding(object):
    def test_delete_delete_projects(self):
        p = subprocess.Popen(
            ["reptor", "project", "--list", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        projects, _ = p.communicate()
        project_titles = [p["name"] for p in json.loads(projects)]

        # Delete dry run without search
        p = subprocess.Popen(
            ["reptor", "deleteprojects"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, lines = p.communicate()
        assert p.returncode == 0
        deleted_projects = [
            line.split(" ", 3)[-1].strip('"')
            for line in lines.decode().splitlines()
            if line.startswith("Would delete")
        ]
        assert all(p in project_titles for p in deleted_projects)

        # Delete dry run with search
        p = subprocess.Popen(
            ["reptor", "deleteprojects", "--title-contains", project_titles[0]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, lines = p.communicate()
        assert p.returncode == 0
        deleted_projects = [
            line.split(" ", 3)[-1].strip('"')
            for line in lines.decode().splitlines()
            if line.startswith("Would delete")
        ]
        assert all(project_titles[0].lower() in p.lower() for p in deleted_projects)

        # Delete dry run with exclude
        p = subprocess.Popen(
            ["reptor", "deleteprojects", "--exclude-title-contains", project_titles[0]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, lines = p.communicate()
        assert p.returncode == 0
        deleted_projects = [
            line.split(" ", 3)[-1].strip('"')
            for line in lines.decode().splitlines()
            if line.startswith("Would delete")
        ]
        assert all(project_titles[0].lower() not in p.lower() for p in deleted_projects)
