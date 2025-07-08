Create findings in your pentest report by JSON or TOML.

## Examples

### Create findings
```bash
cat finding.json | reptor finding
cat finding.toml | reptor finding
```

### Update findings
```bash
cat finding.json | reptor finding --update c46fd6f7-b265-4434-a5b1-872b3b90ab71
cat finding.toml | reptor finding --update c46fd6f7-b265-4434-a5b1-872b3b90ab71
```

The `--update` switch takes the finding ID you want to update (find the ID in the finding URL).

### Sample finding

Upload one finding by using the following structures.  
Use a list to upload multiple findings.

```json title="JSON finding structure"
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

```toml title="TOML finding structure"
status = "in-progress"

[data]
cvss = "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N"
title = "Reflected XSS"
summary = "We detected a reflected XSS vulnerability."
references = [ "https://owasp.org/www-community/attacks/xss/",]
description = "The impact was heavy."
recommendation = "HTML encode user-supplied inputs."
affected_components = [ "https://example.com/alert(1)", "https://example.com/q=alert(1)",]
```

## Usage
```
--8<-- "docs/cli/help-messages/finding"
```
