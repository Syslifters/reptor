The project plugin lets you interact with your SysReptor projects.

## Render Reports
```bash
reptor project --render  # Render report to PDF and download
reptor project --render -o file.pdf  # Save to file.pdf
reptor project --render -o -  # Write to stdout
reptor project --render --upload  # Upload to notes
reptor project --render --design 0222cdf1-4208-491c-8a23-7d49d67707ff  # Render with alternative design
```

You can add the design ID of your alternative design to your `~/.sysreptor/config.yaml`:

```yaml
project:
  design: 0222cdf1-4208-491c-8a23-7d49d67707ff
```

## Export Reports
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
