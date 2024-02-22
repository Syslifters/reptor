Export your project findings as a summary or checklist.

![Export finding checklist](/cli/assets/exportfindings.png)

```bash title="Export findings"
reptor exportfindings  # csv to stdout
reptor exportfindings --format json --output "findings.json"  # json to file
reptor exportfindings --format toml --fieldnames title,cvss  # export custom fieldnames
```

## Usage
```
--8<-- "docs/cli/help-messages/exportfindings"
```
