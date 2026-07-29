"""Provision private project designs for integration tests."""

from __future__ import annotations

import uuid
from typing import Tuple

import requests

from reptor.api.ProjectDesignsAPI import ProjectDesignsAPI
from reptor.api.ProjectsAPI import ProjectsAPI
from reptor.models.ProjectDesign import ProjectDesignField

# Long enough that Translate dry-run stays >1000 chars even when
# executive_summary is skipped, while executive_summary itself still
# contributes so the unskipped count is strictly larger.
_LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
)
INTEGRATION_INTRODUCTION_TEXT = (_LOREM * 20).strip()  # ~1200 chars
INTEGRATION_EXECUTIVE_SUMMARY_TEXT = (_LOREM * 10).strip()  # ~600 chars

# SysReptor report templates use Vue.js, not Django template tags.
MINIMAL_REPORT_TEMPLATE = """<section>
  <h1>{{ report.title }}</h1>
  <div v-for="finding in findings">
    <h2>{{ finding.title }}</h2>
  </div>
</section>
"""

MINIMAL_REPORT_STYLES = """
@page { size: A4; margin: 2cm; }
body { font-family: sans-serif; font-size: 11pt; }
h1 { font-size: 18pt; }
h2 { font-size: 14pt; }
"""

INTEGRATION_FINDING_FIELDS = [
    ProjectDesignField(
        {
            "id": "cvss",
            "type": "cvss",
            "label": "CVSS",
            "required": True,
            "default": "n/a",
        }
    ),
    ProjectDesignField(
        {
            "id": "severity",
            "type": "enum",
            "label": "Severity",
            "required": True,
            "default": None,
            "choices": [
                {"value": "critical", "label": "Critical"},
                {"value": "high", "label": "High"},
                {"value": "medium", "label": "Medium"},
                {"value": "low", "label": "Low"},
                {"value": "info", "label": "Info"},
            ],
        }
    ),
    ProjectDesignField(
        {
            "id": "summary",
            "type": "markdown",
            "label": "Summary",
            "required": True,
            "default": "TODO: High-level summary",
        }
    ),
    ProjectDesignField(
        {
            "id": "description",
            "type": "markdown",
            "label": "Technical Description",
            "required": True,
            "default": "TODO: detailed technical description",
        }
    ),
    ProjectDesignField(
        {
            "id": "recommendation",
            "type": "markdown",
            "label": "Recommendation",
            "required": True,
            "default": "TODO: how to fix the vulnerability",
        }
    ),
    ProjectDesignField(
        {
            "id": "references",
            "type": "list",
            "label": "References",
            "required": False,
            "items": {
                "type": "string",
                "label": "Reference",
                "default": None,
                "required": True,
                "spellcheck": False,
            },
        }
    ),
    ProjectDesignField(
        {
            "id": "affected_components",
            "type": "list",
            "label": "Affected Components",
            "required": True,
            "items": {
                "type": "string",
                "label": "Component",
                "default": "TODO: affected component",
                "required": True,
                "spellcheck": False,
            },
        }
    ),
]

INTEGRATION_REPORT_SECTIONS = [
    {
        "id": "executive_summary",
        "label": "Executive Summary",
        "fields": [
            {
                "id": "executive_summary",
                "type": "markdown",
                "label": "Executive Summary",
                "required": False,
                "default": INTEGRATION_EXECUTIVE_SUMMARY_TEXT,
            }
        ],
    },
    {
        "id": "other",
        "label": "Other",
        "fields": [
            {
                "id": "title",
                "type": "string",
                "label": "Report Title",
                "required": True,
                "default": "Integration Test Report",
                "spellcheck": True,
            },
            {
                "id": "introduction",
                "type": "markdown",
                "label": "Introduction",
                "required": False,
                "default": INTEGRATION_INTRODUCTION_TEXT,
            },
        ],
    },
]


def _unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def create_integration_designs(
    api: ProjectDesignsAPI,
) -> Tuple[str, str]:
    """Create primary (full schema) and alt (minimal) private designs.

    Returns:
        (primary_design_id, alt_design_id)
    """
    suffix = _unique_suffix()
    primary = api.create_project_design(
        name=f"Integration Test Design {suffix}",
        scope="private",
    )
    primary = api.update_project_design(
        project_design_id=primary.id,
        finding_fields=INTEGRATION_FINDING_FIELDS,
        report_sections=INTEGRATION_REPORT_SECTIONS,
        report_template=MINIMAL_REPORT_TEMPLATE,
        report_styles=MINIMAL_REPORT_STYLES,
    )

    alt = api.create_project_design(
        name=f"Integration Test Alt Design {suffix}",
        scope="private",
    )
    alt = api.update_project_design(
        project_design_id=alt.id,
        report_template=MINIMAL_REPORT_TEMPLATE,
        report_styles=MINIMAL_REPORT_STYLES,
    )
    return primary.id, alt.id


def delete_integration_designs(api: ProjectDesignsAPI, *design_ids: str) -> None:
    """Delete designs by ID, ignoring missing resources."""
    for design_id in design_ids:
        if not design_id:
            continue
        try:
            api.delete_project_design(project_design_id=design_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response is None or exc.response.status_code != 404:
                raise


def seed_integration_report_content(projects_api: ProjectsAPI) -> None:
    """Ensure report sections have enough text for Translate dry-run asserts."""
    projects_api.update_section(
        "executive_summary",
        {"data": {"executive_summary": INTEGRATION_EXECUTIVE_SUMMARY_TEXT}},
    )
    projects_api.update_section(
        "other",
        {
            "data": {
                "title": "Integration Test Report",
                "introduction": INTEGRATION_INTRODUCTION_TEXT,
            }
        },
    )
