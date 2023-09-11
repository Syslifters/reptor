The project plugin lets you interact with your SysReptor projects.

## Examples
```bash title="Render reports"
reptor project --render  # Render report to PDF and download
reptor project --render -o file.pdf  # Render report and save to file.pdf
reptor project --render -o -  # Render report to PDF and write to stdout
reptor project --render --upload  # Render report and upload to notes
```

```bash title="Export reports"
reptor project --export archive  # Export your report to tar.gz
reptor project --export archive -o -  # Export your report to tar.gz, write to stdout
reptor project --export json
reptor project --export toml -o -  # Write report as toml to stdout
reptor project --export yaml --upload  # Export report as yaml and upload to notes
```

## Usage
```
--8<-- "docs/cli/help-messages/project"
```
