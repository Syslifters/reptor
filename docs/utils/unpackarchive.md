`unpackarchive` unpacks exported tar.gz archives (like exported projects, designs, finding templates) to json or toml structures. Use `packarchive` to convert back to tar.gz.

## Examples
```bash title="Unpack archive"
reptor unpackarchive --format json --output project ./project.tar.gz  # Unpack project archive as json to "project" directory
reptor unpackarchive --format toml --output design ./design.tar.gz  # Unpack design archive as toml to "design" directory
```

## Usage
```
--8<-- "docs/cli/help-messages/unpackarchive"
```
