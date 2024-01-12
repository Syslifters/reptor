`packarchive` packs unpacked toml and json data structures back to tar.gz archives. Use `unpackarchive` to unpack tar.gz archives (like exported projects, designs, finding templates).

## Examples
```bash title="Pack archive"
reptor packarchive --output project.tar.gz ./project  # Pack contents of "project" directory to project.tar.gz
```

## Usage
```
--8<-- "docs/cli/help-messages/packarchive"
```
