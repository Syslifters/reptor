import json
import os
import uuid
from unittest.mock import MagicMock, Mock, patch

import pytest
from requests.exceptions import HTTPError

from reptor.lib.reptor import reptor
from reptor.models.FindingTemplate import FindingTemplate
from reptor.models.Project import Project
from reptor.models.ProjectDesign import ProjectDesign

from ..FindingFromTemplate import FindingFromTemplate


class TestFinding:
    finding_template = json.loads(
        open(
            os.path.join(os.path.dirname(__file__), "./data/finding_template.json")
        ).read()
    )

    @pytest.fixture(autouse=True)
    def setup(self):
        self.reptor = reptor
        self.finding_from_template = FindingFromTemplate()

    @pytest.mark.parametrize(
        ["template_id", "raises"],
        [
            ("template_id", True),
            ("1", True),
            (str(uuid.uuid1()), False),
            (str(uuid.uuid3(uuid.NAMESPACE_DNS, "example")), False),
            (str(uuid.uuid4()), False),
            (str(uuid.uuid5(uuid.NAMESPACE_DNS, "example")), False),
        ],
    )
    def test_get_template_by_id(self, template_id, raises):
        self.reptor.api._templates = MagicMock()
        with patch.object(
            self.finding_from_template.reptor.api.templates,
            "get_template",
            side_effect=HTTPError(response=Mock(status_code=404)),
        ) as mock_get_template:
            if raises:
                with pytest.raises(ValueError):
                    self.finding_from_template._get_template_by_id(template_id)
                mock_get_template.assert_not_called()
            else:
                with pytest.raises(KeyError):
                    # If uuid check passses, template doesn't exist
                    self.finding_from_template._get_template_by_id(template_id)
                mock_get_template.assert_called_once()

                # Reset mock and test with existing template
                mock_get_template.reset_mock()
                mock_get_template.side_effect = None
                mock_get_template.return_value = FindingTemplate(self.finding_template)
                assert self.finding_from_template._get_template_by_id(template_id)
                mock_get_template.assert_called_once()

    @pytest.mark.parametrize(
        ["tags", "found"],
        [
            (["tag1"], False),
            (["web"], True),
            (["web", "tag1"], False),
        ],
    )
    def test_get_templates_by_tag(self, tags, found):
        self.reptor.api._templates = MagicMock()
        self.finding_from_template.reptor.api.templates.get_templates_by_tag = (
            MagicMock(return_value=[FindingTemplate(self.finding_template)])
        )
        if not found:
            with pytest.raises(KeyError):
                self.finding_from_template._get_templates_by_tags(tags)
        else:
            assert self.finding_from_template._get_templates_by_tags(tags)

    @pytest.mark.parametrize(
        ["project_language", "expected_language", "expected_index"],
        [
            ("en-US", "en-US", 0),
            ("de-DE", "de-DE", 1),
            ("fr-FR", "en-US", 0),  # Fallback to main translation
            ("", "en-US", 0),
        ],
    )
    def test_get_template_translation(
        self, project_language, expected_language, expected_index
    ):
        self.reptor.api._projects = MagicMock()
        self.reptor.api.projects.project.language = project_language
        assert self.reptor.api.projects.project.language == project_language
        template = FindingTemplate(self.finding_template)
        assert self.finding_from_template._get_template_translation(template) == (
            expected_index,
            expected_language,
        )
        del self.reptor.api.projects.project  # clear cached property
