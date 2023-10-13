Export your project findings as a summary or checklist.

![Export finding checklist](/cli/assets/projectfindings.png)

```bash title="Export findings"
reptor projectfindings  # csv to stdout
reptor projectfindings --format json --output "findings.json"  # json to file
reptor projectfindings --format toml --fieldnames title,cvss  # export custom fieldnames
```

## Usage
```
--8<-- "docs/cli/help-messages/projectfindings"
```
