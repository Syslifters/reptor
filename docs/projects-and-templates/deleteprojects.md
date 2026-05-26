# DeleteProjects

Delete SysReptor projects.  
Dry run is default: No projects are deleted unless you specify `--no-dry-run`.

## Example
```shell
reptor deleteprojects --title-contains "delete me"  # Delete projects matching the search query
reptor deleteprojects --exclude-title-contains "leave me"  # Exclude projects with search query
reptor deleteprojects --no-dry-run  # Delete all projects, no dry run
```

## Usage
<<< @/cli/help-messages/deleteprojects{txt}
