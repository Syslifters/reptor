Create new findings from finding templates by template ID or tag.  
Specifying a tag might create multiple findings. Tags can be comma-separated and are `and`-connected.

If a finding exists in the report that was created from a finding template, it is not newly added.

## Examples
```bash
reptor findingfromtemplate --template-id 8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e
reptor findingfromtemplate --tags web
reptor findingfromtemplate --tags web,sql  # Create findings from templates that have both tags "web" and "sql"
```

## Usage
```
--8<-- "docs/cli/help-messages/findingfromtemplate"
```
