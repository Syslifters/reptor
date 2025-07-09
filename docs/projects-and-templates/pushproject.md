Push project data (section and finding data) to your pentest report by JSON or TOML.

## Example
```bash
cat project.json | reptor pushproject
cat project.toml | reptor pushproject
```

If to push your data to a new report, create a project beforehand.

```bash
reptor createproject --name "New project" --design "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e"
cat project.json | reptor pushproject
```

## Sample project

Upload project data by using the following structures.  
You can add data to your report sections and create or update findings.

If a finding has an `id`, reptor will update the finding instead of creating it.


```toml title="Project structure in JSON"
{
  "sections": [
    { 
      "status": "finished",
      "data": {
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
      }
    }
  ],
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
```

```toml title="Project structure in TOML"
[[sections]]
status = "finished"

[sections.data]
title = "Report title"
customer_name = "GotBreached Ltd."
receiver_name = "Maxima Doe"
executive_summary = "This is the Executive Summary\n"
report_date = "2022-04-25"
list_of_changes = [
    { description = "Draft", date = "2022-04-22", version = "0.1" },
    { description = "Final Report", date = "2022-04-25", version = "1.0" },
]

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

## Usage
```
--8<-- "docs/cli/help-messages/pushproject"
```
