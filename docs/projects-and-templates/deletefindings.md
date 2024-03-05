Delete findings from your project.  
Dry run is default: No findings are deleted unless you specify `--no-dry-run`.

## Example
```bash
reptor deletefindings --title-contains "delete me"  # Delete findings matching the search query
reptor deletefindings --exclude-title-contains "leave me"  # Exclude findings with search query
reptor deletefindings --no-dry-run  # Delete all findings, no dry run
```

## Usage
```
--8<-- "docs/cli/help-messages/deletefindings"
```
