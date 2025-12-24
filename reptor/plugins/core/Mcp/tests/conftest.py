import pytest
from unittest.mock import MagicMock
from reptor.models.Finding import FindingRaw
from reptor.models.FindingTemplate import FindingTemplate
from reptor.models.ProjectDesign import ProjectDesign


@pytest.fixture
def mock_reptor():
    """Mock Reptor instance with standard configuration."""
    mock = MagicMock()
    mock.get_active_project_id.return_value = "test-project-id"
    return mock


@pytest.fixture
def anonymizer():
    """Fresh Anonymizer instance for each test."""
    from reptor.plugins.core.Mcp.Anonymizer import Anonymizer
    return Anonymizer()


@pytest.fixture
def project_id():
    """Standard test project ID."""
    return "test-project-id"


@pytest.fixture
def sample_finding_data():
    """Standard finding data for testing."""
    return {
        "id": "f1",
        "status": "in-progress",
        "data": {
            "title": "SQL Injection",
            "severity": "high",
            "cvss": "8.8",
            "affected_components": ["192.168.1.5"]
        }
    }


@pytest.fixture
def sample_finding_raw(sample_finding_data):
    """FindingRaw instance with sample data."""
    return FindingRaw(sample_finding_data)


@pytest.fixture
def sample_template_data():
    """Standard template data for testing."""
    mock_template = MagicMock(spec=FindingTemplate)
    mock_template.id = "t1"
    mock_template.get_main_title.return_value = "Template 1"
    mock_template.source = MagicMock(value="created")
    mock_template.tags = ["web"]
    mock_template.to_dict.return_value = {"id": "t1", "tags": ["web"]}
    return mock_template


@pytest.fixture
def sample_project_design():
    """Mock ProjectDesign with common field types."""
    mock_design = MagicMock(spec=ProjectDesign)

    # Title field (string, required)
    mock_title_field = MagicMock()
    mock_title_field.id = "title"
    mock_title_field.type = MagicMock(value="string")
    mock_title_field.label = "Title"
    mock_title_field.required = True
    mock_title_field.choices = []
    mock_title_field.items = None
    mock_title_field.properties = None

    # Severity field (enum, required)
    mock_severity_field = MagicMock()
    mock_severity_field.id = "severity"
    mock_severity_field.type = MagicMock(value="enum")
    mock_severity_field.label = "Severity"
    mock_severity_field.required = True
    mock_severity_field.choices = [
        {"value": "info", "label": "Info"},
        {"value": "low", "label": "Low"},
        {"value": "medium", "label": "Medium"},
        {"value": "high", "label": "High"},
        {"value": "critical", "label": "Critical"}
    ]
    mock_severity_field.items = None
    mock_severity_field.properties = None

    # Description field (markdown, optional)
    mock_description_field = MagicMock()
    mock_description_field.id = "description"
    mock_description_field.type = MagicMock(value="markdown")
    mock_description_field.label = "Description"
    mock_description_field.required = False
    mock_description_field.choices = []
    mock_description_field.items = None
    mock_description_field.properties = None

    mock_design.finding_fields = [mock_title_field, mock_severity_field, mock_description_field]
    return mock_design
