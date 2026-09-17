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
pipx inject --force reptor 'reptor[translate]'
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

```usage: reptor [-h] [-s SERVER] [-t TOKEN] [-k] [-p PROJECT_ID]
              [--timeout SECONDS] [--personal-note] [-v] [--debug]
              [-n NOTETITLE] [--no-timestamp] [--file FILE]

Examples:
                reptor conf
                echo "Upload this!" | reptor note
                reptor file data/*
                cat sslyze.json | reptor sslyze --json --push-findings
                reptor nmap --xml --upload -i nmap.xml

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity (> INFO)
  --debug               sets logging to DEBUG
  -n NOTETITLE, --notetitle NOTETITLE
  --no-timestamp        do not prepend timestamp to note
  --file FILE           Local file to read

subcommands:
  
  Core:
   conf                  Shows config and sets config
   mcp                   Starts the Model Context Protocol (MCP) server
   plugins               Allows plugin management & development
  
  Projects & Templates:
   ai                    Process report sections using OpenAI with dynamic skill selection
   createproject         Create a new pentest project
   deletefindings        Deletes findings by title
   deleteprojects        Deletes projects by title
   exportfindings        Export your project findings as a summary or checklist
   file                  Uploads a file
   finding               Uploads findings from JSON or TOML
   findingfromtemplate   Creates findings from remote finding templates
   note                  Uploads and lists notes
   project               Work with projects
   pushproject           Push data to project from JSON or TOML
   template              Queries Finding Templates from SysReptor
   translate             Translate Projects to other languages via Deepl
  
  Tools:
   burp                  Burp vulnerability importer
   nessus                Nessus vulnerability importer
   nmap                  format nmap output
   openvas               OpenVAS vulnerability importer
   qualys                Qualys vulnerability importer
   sslyze                format sslyze JSON output
   zap                   Parses ZAP reports (JSON, XML)
  
  Importers:
   defectdojo            Imports DefectDojo finding templates
   ghostwriter           Imports GhostWriter finding templates
   importers             Show importers to use to import finding templates
  
  Utils:
   packarchive           Pack directories into a .tar.gz file
   unpackarchive         Unpack .tar.gz exported archives

configuration:
  -s SERVER, --server SERVER
  -t TOKEN, --token TOKEN
                        SysReptor API token
  -k, --insecure        do not verify server certificate
  -p PROJECT_ID, --project-id PROJECT_ID
                        SysReptor project ID
  --timeout SECONDS     HTTP request timeout in seconds (default: 30)
  --personal-note       add notes to personal notes

```