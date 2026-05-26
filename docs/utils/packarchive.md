# Packarchive

`packarchive` packs unpacked toml and json data structures back to tar.gz archives. Use `unpackarchive` to unpack tar.gz archives (like exported projects, designs, finding templates).

## Examples
```shell
reptor packarchive --output project.tar.gz ./project  # Pack contents of "project" directory to project.tar.gz
```

## Usage
<<< @/cli/help-messages/packarchive{txt}
