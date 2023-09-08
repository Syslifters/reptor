The project plugin lets you interact with your SysReptor projects.

## Examples
```bash title="Render reports"
reptor project --render  # Render report to PDF and download
reptor project --render -o -  # Render report to PDF and write to stdout
```

```bash title="Render reports"
reptor project --export archive  # Export your report to tar.gz
reptor project --export archive -o -  # Export your report to tar.gz, write to stdout
reptor project --export json  # Export your report as json
reptor project --export toml  # Export your report as toml
reptor project --export yaml  # Export your report as yaml
```

## Usage
```
--8<-- "docs/cli/help-messages/project"
```
