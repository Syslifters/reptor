Create a new pentest project via CLI.

This module updates your reptor config with the newly created project ID, so you can immediately continue with other commands.   
Use `--no-update-config` to prevent this behavior.

## Examples
```bash
reptor createproject --name "New project" --design "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e" --tags web,auto
reptor createproject --name "New project" --design "8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e" --no-update-config
```

## Usage
```
--8<-- "docs/cli/help-messages/createproject"
```
