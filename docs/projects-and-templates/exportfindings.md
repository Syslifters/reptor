# ExportFindings

Export your project findings as a summary or checklist.

```shell
reptor exportfindings  # csv to stdout
reptor exportfindings --format json --output "findings.json"  # json to file
reptor exportfindings --format toml --fieldnames title,cvss  # export custom fieldnames
```

## Usage
<<< @/cli/help-messages/exportfindings{txt}
