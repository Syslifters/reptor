# reptor
`reptor` allows you to automate pentest reporting with SysReptor.

You can use `reptor` as a command line (CLI) tool:

```shell
reptor exportfindings --format json
```

Or use it as a Python library:

```python
from reptor import Reptor

reptor = Reptor(
    server=os.environ.get("REPTOR_SERVER"),
    token=os.environ.get("REPTOR_TOKEN"),
    project_id="41c09e60-44f1-453b-98f3-3f1875fe90fe",
)
reptor.api.projects.get_project()
```

You can use it to:

 * Create findings and notes from tool outputs
 * Upload evidences (also bulk upload)
 * Import data from other reporting tools
 * Manage projects
 * Read, update, create findings
 * Download PDF reports
 * Read, update, create notes
 * Export notes as PDF
 * and more...

**GitHub:** <https://github.com/Syslifters/reptor/>  
**Python Library Docs:** <https://docs.sysreptor.com/python-library/>   
**CLI Docs:** <https://docs.sysreptor.com/cli/getting-started/>   
**PyPi:** <https://pypi.org/project/reptor/>   

## Prerequisites

* Python 3.10-3.14
* pipx

Install pipx ([guide](https://pipx.pypa.io/stable/how-to/install-pipx.html)). Open a new shell after `pipx ensurepath`.

```shell
# macOS
brew install pipx
pipx ensurepath

# Ubuntu/Debian
sudo apt update && sudo apt install pipx
pipx ensurepath

# Fedora
sudo dnf install pipx
pipx ensurepath

# Windows (pip)
py -m pip install --user pipx
py -m pipx ensurepath
```

## Installation
### From pypi
```shell
pipx install reptor
```

#### Optional dependencies
* translate (requires deepl)
* ghostwriter (requires gql)
* ai (requires openai)
* mcp (requires mcp)
* dev (requires pytest)

Inject extras into an existing install (`--force` is required because pipx otherwise skips `reptor`, which is already installed):

```shell
pipx inject --force reptor 'reptor[mcp]'
pipx inject --force reptor 'reptor[all]'
```

Or install with extras from the start: `pipx install 'reptor[translate]'` or `pipx install 'reptor[all]'`.

### From source
```shell
git clone https://github.com/Syslifters/reptor.git
cd reptor
pipx install .
```

Install [optional dependencies](#optional-dependencies) by `pipx install '.[all]'` or `pipx inject --force reptor 'reptor[all]'`.

### From BlackArch

```shell
pacman -S reptor
```

[![BlackArch package](https://repology.org/badge/version-for-repo/blackarch/reptor.svg)](https://repology.org/project/reptor/versions)


### Usage
<<< @/cli/help-messages/reptor{txt}
