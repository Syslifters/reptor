import pathlib

BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent

PERSONAL_SYSREPTOR_HOME: pathlib.Path = pathlib.Path.home() / ".sysreptor"
PERSONAL_CONFIG_FILE: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "config.yaml"

PLUGIN_DIRS: pathlib.Path = BASE_DIR / "plugins"

PLUGIN_DIRS_CORE: pathlib.Path = PLUGIN_DIRS / "core"
PLUGIN_DIRS_TOOLS: pathlib.Path = PLUGIN_DIRS / "tools"
PLUGIN_DIRS_PROJECTS: pathlib.Path = PLUGIN_DIRS / "projects"
PLUGIN_DIRS_UPLOADS: pathlib.Path = PLUGIN_DIRS / "uploads"
PLUGIN_DIRS_IMPORTERS: pathlib.Path = PLUGIN_DIRS / "importers"
PLUGIN_DIRS_EXPORTERS: pathlib.Path = PLUGIN_DIRS / "exporters"
PLUGIN_DIRS_UTILS: pathlib.Path = PLUGIN_DIRS / "utils"
PLUGIN_DIRS_USER: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "plugins"

PLUGIN_IMPORT_DIRS = [
    PLUGIN_DIRS_CORE,
    PLUGIN_DIRS_TOOLS,
    PLUGIN_DIRS_PROJECTS,
    PLUGIN_DIRS_UPLOADS,
    PLUGIN_DIRS_IMPORTERS,
    PLUGIN_DIRS_EXPORTERS,
    PLUGIN_DIRS_UTILS,
    PLUGIN_DIRS_USER,  # Should be last to override other plugins
]

PLUGIN_TEMPLATES_DIR_NAME: str = "templates"
FINDING_TEMPLATES_DIR_NAME: str = "findings"

PLUGIN_TOOLBASE_TEMPLATE_FOLDER: pathlib.Path = BASE_DIR / "templates" / "Toolbase"

LOG_FOLDER: pathlib.Path = PERSONAL_SYSREPTOR_HOME / "logs"

NEWLINE = "\n"

USER_AGENT = "reptor CLI v0.1.0"  # TODO dynamic version
LANGUAGE_CODE = "en"
FORMAT_MODULE_PATH = []
LOCALE_PATHS = (
    'locale',
)
USE_THOUSAND_SEPARATOR = False
USE_L10N = False
USE_I18N = False
USE_THOUSAND_SEPARATOR = False
DECIMAL_SEPARATOR = "."
THOUSAND_SEPARATOR = ","
NUMBER_GROUPING = 0

# Django Related Setup
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "libraries": {
                "md": "reptor.utils.templatetags.md",
            },
        },
    },
]

DEBUG = True
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = None
USE_I18N = True
INSTALLED_APPS = []
LOGGING_CONFIG = []
LOGGING = []
FORCE_SCRIPT_NAME = ""

DEFAULT_PROJECT_DESIGN = {
    "report_sections": [
        {"id": "other", "label": "Other", "fields": [
            {
                "id": "title",
                "type": "string",
                "label": "Title",
                "origin": "core",
                "default": "TODO: Report Title",
                "required": True,
                "spellcheck": True,
            }
        ]},
    ],
    "finding_fields": [
        {
            "id": "cvss",
            "type": "cvss",
            "label": "CVSS",
            "origin": "predefined",
            "default": "n/a",
            "required": True,
        },
        {
            "id": "title",
            "type": "string",
            "label": "Title",
            "origin": "core",
            "default": "TODO: Finding Title",
            "required": True,
            "spellcheck": True,
        },
        {
            "id": "impact",
            "type": "markdown",
            "label": "Impact",
            "origin": "predefined",
            "default": "TODO: impact of finding",
            "required": True,
        },
        {
            "id": "summary",
            "type": "markdown",
            "label": "Summary",
            "origin": "predefined",
            "default": "TODO: High-level summary",
            "required": True,
        },
        {
            "id": "severity",
            "type": "enum",
            "label": "Severity",
            "origin": "predefined",
            "choices": [
                {"label": "Info", "value": "info"},
                {"label": "Low", "value": "low"},
                {"label": "Medium", "value": "medium"},
                {"label": "High", "value": "high"},
                {"label": "Critical", "value": "critical"},
            ],
            "default": None,
            "required": True,
        },
        {
            "id": "references",
            "type": "list",
            "items": {
                "type": "string",
                "label": "Reference",
                "origin": "predefined",
                "default": None,
                "required": True,
                "spellcheck": False,
            },
            "label": "References",
            "origin": "predefined",
            "required": False,
        },
        {
            "id": "description",
            "type": "markdown",
            "label": "Technical Description",
            "origin": "predefined",
            "default": "TODO: detailed technical description what this findings is about and how it can be exploited",
            "required": True,
        },
        {
            "id": "precondition",
            "type": "string",
            "label": "Precondition",
            "origin": "predefined",
            "default": None,
            "required": True,
            "spellcheck": True,
        },
        {
            "id": "retest_notes",
            "type": "markdown",
            "label": "Re-test Notes",
            "origin": "predefined",
            "default": None,
            "required": False,
        },
        {
            "id": "retest_status",
            "type": "enum",
            "label": "Re-test Status",
            "origin": "predefined",
            "choices": [
                {"label": "Open", "value": "open"},
                {"label": "Resolved", "value": "resolved"},
                {"label": "Partially Resolved", "value": "partial"},
                {"label": "Changed", "value": "changed"},
                {"label": "Accepted", "value": "accepted"},
                {"label": "New", "value": "new"},
            ],
            "default": None,
            "required": False,
        },
        {
            "id": "wstg_category",
            "type": "enum",
            "label": "OWASP Web Security Testing Guide Category",
            "origin": "predefined",
            "choices": [
                {"label": "INFO - Information Gathering", "value": "INFO"},
                {
                    "label": "CONF - Configuration and Deployment Management",
                    "value": "CONF",
                },
                {"label": "IDNT - Identity Management", "value": "IDNT"},
                {"label": "ATHN - Authentication", "value": "ATHN"},
                {"label": "ATHZ - Authorization", "value": "ATHZ"},
                {"label": "SESS - Session Management", "value": "SESS"},
                {"label": "INPV - Input Validation", "value": "INPV"},
                {"label": "ERRH - Error Handling", "value": "ERRH"},
                {"label": "CRYP - Weak Cryptography", "value": "CRYP"},
                {"label": "BUSL - Business Logic", "value": "BUSL"},
                {"label": "CLNT - Client-side Testing", "value": "CLNT"},
                {"label": "APIT - API Testing", "value": "APIT"},
            ],
            "default": None,
            "required": True,
        },
        {
            "id": "recommendation",
            "type": "markdown",
            "label": "Recommendation",
            "origin": "predefined",
            "default": "TODO: how to fix the vulnerability",
            "required": True,
        },
        {
            "id": "owasp_top10_2021",
            "type": "enum",
            "label": "OWASP Top 10 - 2021",
            "origin": "predefined",
            "choices": [
                {"label": "A01:2021 - Broken Access Control", "value": "A01_2021"},
                {"label": "A02:2021 - Cryptographic Failures", "value": "A02_2021"},
                {"label": "A03:2021 - Injection", "value": "A03_2021"},
                {"label": "A04:2021 - Insecure Design", "value": "A04_2021"},
                {"label": "A05:2021 - Security Misconfiguration", "value": "A05_2021"},
                {
                    "label": "A06:2021 - Vulnerable and Outdated Components",
                    "value": "A06_2021",
                },
                {
                    "label": "A07:2021 - Identification and Authentication Failures",
                    "value": "A07_2021",
                },
                {
                    "label": "A08:2021 - Software and Data Integrity Failures",
                    "value": "A08_2021",
                },
                {
                    "label": "A09:2021 - Security Logging and Monitoring Failures",
                    "value": "A09_2021",
                },
                {
                    "label": "A10:2021 - Server-Side Request Forgery (SSRF)",
                    "value": "A10_2021",
                },
            ],
            "default": None,
            "required": True,
        },
        {
            "id": "affected_components",
            "type": "list",
            "items": {
                "id": "",
                "type": "string",
                "label": "Component",
                "origin": "predefined",
                "default": "TODO: affected component",
                "required": True,
                "spellcheck": False,
            },
            "label": "Affected Components",
            "origin": "predefined",
            "required": True,
        },
        {
            "id": "short_recommendation",
            "type": "string",
            "label": "Short Recommendation",
            "origin": "predefined",
            "default": "TODO: short recommendation",
            "required": True,
            "spellcheck": False,
        },
        {
            "id": "cwe",
            "type": "cwe",
            "label": "CWE",
            "origin": "custom",
            "default": None,
            "required": False,
        },
        {
            "id": "number_field_1",
            "type": "number",
            "label": "Static Number",
            "origin": "predefined",
            "default": None,
            "maximum": None,
            "minimum": None,
            "required": False,
            "help_text": None
        },
        {
            "id": "number_field_2",
            "type": "number",
            "label": "Dynamic Number",
            "origin": "predefined",
            "default": None,
            "maximum": None,
            "minimum": None,
            "required": False,
            "help_text": None
        },
        {
            "id": "boolean_field_1",
            "type": "boolean",
            "label": "Boolean Field",
            "origin": "predefined",
        },
        {
            "id": "boolean_field_2",
            "type": "boolean",
            "label": "Boolean Field",
            "origin": "predefined",
        },
    ],
}
