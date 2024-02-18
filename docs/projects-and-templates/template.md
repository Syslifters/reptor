Upload and query Finding Templates from SysReptor

## Upload finding templates

```bash
cat template.json | reptor template
cat template.toml | reptor template
```

### Sample finding template

Upload one finding template by using the following structures.  
Use a list to upload multiple finding templates.

```json title="JSON finding template structure"
{
  "tags": [
    "web"
  ],
  "translations": [
    {
      "language": "en-US",
      "is_main": true,
      "status": "finished",
      "data": {
        "title": "My Title",
        "description": "My Description"
      }
    }
  ]
}
```

```toml title="TOML finding template structure"
tags = [
    "web",
]

[[translations]]
is_main = true
language = "en-US"
status = "finished"

[translations.data]
title = "My title"
description = "My description"
```

## Read finding templates
```
reptor template --list  # template overview
reptor template --search SQL  # template overview, search for keywords
reptor template --search SQL --export plain  # print templates for copy&paste
reptor template --search SQL --export plain --language en  # filter for language
reptor template --export json  # export templates as json
reptor template --search SQL --export json  # search for keyword
reptor template --export tar.gz  # export all templates as tar.gz (importable via SysReptor web interface)
```

## Usage
```
--8<-- "docs/cli/help-messages/template"
```
