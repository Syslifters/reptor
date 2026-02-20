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
def field_excluder():
    """Fresh FieldExcluder instance for each test."""
    from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder

    return FieldExcluder(exclude_fields=["affected_components"])


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
            "affected_components": ["192.168.1.5"],
        },
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
        {"value": "critical", "label": "Critical"},
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

    mock_design.finding_fields = [
        mock_title_field,
        mock_severity_field,
        mock_description_field,
    ]
    return mock_design


@pytest.fixture
def sample_section_data():
    """Standard section data for testing."""
    return {
        "id": "executive_summary",
        "label": "Executive Summary",
        "status": "in-progress",
        "data": {
            "executive_summary": "This is a test summary",
            "affected_components": ["192.168.1.1"],
        },
    }


@pytest.fixture
def sample_section_raw(sample_section_data):
    """SectionRaw instance with sample data."""
    from reptor.models.Section import SectionRaw

    return SectionRaw(sample_section_data)


@pytest.fixture
def sample_project_design_with_report_fields():
    """Mock ProjectDesign with report fields for testing get_project_schema."""
    mock_design = MagicMock(spec=ProjectDesign)

    # Executive summary field (string)
    mock_exec_field = MagicMock()
    mock_exec_field.id = "executive_summary"
    mock_exec_field.type = MagicMock(value="string")
    mock_exec_field.label = "Executive Summary"
    mock_exec_field.required = True
    mock_exec_field.choices = []
    mock_exec_field.items = None
    mock_exec_field.properties = None

    # Scope field (markdown)
    mock_scope_field = MagicMock()
    mock_scope_field.id = "scope"
    mock_scope_field.type = MagicMock(value="markdown")
    mock_scope_field.label = "Scope"
    mock_scope_field.required = False
    mock_scope_field.choices = []
    mock_scope_field.items = None
    mock_scope_field.properties = None

    # Test methodology field (enum)
    mock_method_field = MagicMock()
    mock_method_field.id = "test_methodology"
    mock_method_field.type = MagicMock(value="enum")
    mock_method_field.label = "Test Methodology"
    mock_method_field.required = True
    mock_method_field.choices = [
        {"value": "blackbox", "label": "Black Box"},
        {"value": "whitebox", "label": "White Box"},
    ]
    mock_method_field.items = None
    mock_method_field.properties = None

    mock_design.report_fields = [
        mock_exec_field,
        mock_scope_field,
        mock_method_field,
    ]
    return mock_design
