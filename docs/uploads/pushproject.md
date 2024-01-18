Push project data (section and finding data) to your pentest report by JSON or TOML.

## Example
```bash
cat project.json | reptor pushproject
cat project.toml | reptor pushproject
```

## Sample project

Upload project data by using the following structures.  
You can add data to your report sections and create findings.

```json title="TOML project structure"
{
  "status": "in-progress",
  "data": {
    "cvss": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N",
    "title": "Reflected XSS",
    "summary": "We detected a reflected XSS vulnerability.",
    "references": [
      "https://owasp.org/www-community/attacks/xss/"
    ],
    "description": "The impact was heavy.",
    "recommendation": "HTML encode user-supplied inputs.",
    "affected_components": [
      "https://example.com/alert(1)",
      "https://example.com/q=alert(1)"
    ]
  }
}
```

```toml title="Project structure in TOML"
[report_data]
title = "Report title"
customer_name = "GotBreached Ltd."
receiver_name = "Maxima Doe"
executive_summary = """
This is the Executive Summary
"""
report_date = "2024-04-25"

[[report_data.list_of_changes]]
description = "Draft"
date = "2024-04-22"
version = "0.1"

[[report_data.list_of_changes]]
description = "Final Report"
date = "2024-04-25"
version = "1.0"

[[findings]]
status = "in-progress"

[findings.data]
title = "Session management weaknesses"
cvss = "CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N"
summary = "My Summary"
affected_components = [
    "example.com",
]

[[findings]]
status = "finished"
[findings.data]
title = "Untrusted TLS certificates"
cvss = "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N"
summary = "Summary"
recommendation = ""
affected_components = [
    "example.com",
]
```

```toml title="Project structure in JSON"
{
  "report_data": {
    "title": "Report title",
    "customer_name": "GotBreached Ltd.",
    "receiver_name": "Maxima Doe",
    "executive_summary": "This is the Executive Summary\n",
    "report_date": "2022-04-25",
    "list_of_changes": [
      {
        "description": "Draft",
        "date": "2022-04-22",
        "version": "0.1"
      },
      {
        "description": "Final Report",
        "date": "2022-04-25",
        "version": "1.0"
      }
    ]
  },
  "findings": [
    {
      "status": "in-progress",
      "data": {
        "title": "Session management weaknesses",
        "cvss": "CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N",
        "summary": "My Summary",
        "affected_components": [
          "example.com"
        ]
      }
    },
    {
      "status": "finished",
      "data": {
        "title": "Untrusted TLS certificates",
        "cvss": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N",
        "summary": "Summary",
        "recommendation": "",
        "affected_components": [
          "example.com"
        ]
      }
    }
  ]
}

## Usage
```
--8<-- "docs/cli/help-messages/pushproject"
```
