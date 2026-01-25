# reptor
`reptor` allows you to automate pentest reporting with SysReptor.

You can use `reptor` as a command line (CLI) tool:

```python title="Export your findings as json from the CLI"
reptor exportfindings --format json
```

Or use it as a Python library:

```python title="Fetch project in Python script"
from reptor import Reptor

reptor = Reptor(
    server=os.environ.get("REPTOR_SERVER"),
    token=os.environ.get("REPTOR_TOKEN"),
    project_id="41c09e60-44f1-453b-98f3-3f1875fe90fe",
)
reptor.api.projects.fetch_project()
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
 * Model Context Protocol (MCP): Connect SysReptor to AI agents.
 * and more...

**GitHub:** [https://github.com/Syslifters/reptor/](https://github.com/Syslifters/reptor/)  
**Python Library Docs:** [https://docs.sysreptor.com/python-library/](https://docs.sysreptor.com/python-library/)   
**CLI Docs:** [https://docs.sysreptor.com/cli/getting-started/](https://docs.sysreptor.com/cli/getting-started/)   
**PyPi:** [https://pypi.org/project/reptor/](https://pypi.org/project/reptor/)   

## Prerequisites

* Python 3.10-3.14
* pip3

## Installation
### From pypi
`pip3 install reptor`

#### Optional dependencies
* translate (requires deepl)
* ghostwriter (requires gql)
* mcp (requires mcp)
* dev (requires pytest)

Install by `pip3 install reptor[translate]`.  
Install all optional dependencies using `pip3 install reptor[all]`

### From source
```
git clone https://github.com/Syslifters/reptor.git
cd reptor
pip3 install .
```

Install [optional dependencies](#optional-dependencies) by `pip3 install .[all]`.

### From BlackArch

```
pacman -S reptor
```

[![BlackArch package](https://repology.org/badge/version-for-repo/blackarch/reptor.svg)](https://repology.org/project/reptor/versions)


### Usage

```usage: reptor [-h] [-s SERVER] [-t TOKEN] [-k] [-p PROJECT_ID]
              [--personal-note] [-v] [--debug] [-n NOTETITLE] [--no-timestamp]
              [--file FILE]

Examples:
                reptor conf
                echo "Upload this!" | reptor note
                reptor file data/*
                cat sslyze.json | reptor sslyze --json --push-findings
                reptor nmap --xml --upload -i nmap.xml

optional arguments:
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
  --personal-note       add notes to personal notes

```

## Model Context Protocol (MCP)

Reptor can act as an MCP server, allowing AI agents to interact with your SysReptor instance.

### General Configuration

Most MCP-compatible AI tools and agents (e.g., Claude Desktop, Cursor, IDE extensions) use a standard JSON configuration. Add the following to your tool's MCP settings:

```json
{
  "mcpServers": {
    "reptor": {
      "command": "reptor",
      "args": ["mcp", "--remove-fields=affected_components"]
    }
  }
}
```

### Setup for gemini-cli

To add the server to `gemini-cli`, use the `mcp add` command:

```bash
gemini mcp add reptor reptor mcp --remove-fields=affected_components
```

### Setup for Claude Code

Run the following command:

```bash
claude mcp add reptor -- reptor mcp --remove-fields=affected_components
```

### Field Removal

The `--remove-fields` flag allows you to exclude specific fields from findings before they are sent to the LLM. This is useful for preventing sensitive data from being exposed to AI agents.

#### Usage

Specify fields to remove as a comma-separated list:

```bash
reptor mcp --remove-fields=affected_components,internal_notes
```

#### Common Field Names

- `affected_components`: Lists affected hosts, IPs, URLs
- `internal_notes`: Internal notes not meant for LLM consumption
- `evidence`: File attachments and evidence data
- `recommendation`: Remediation steps (optional)

#### Field Removal Scope

**Important:** The `--remove-fields` flag only removes the specified fields from data sent to the LLM. Fields are completely excluded, not masked.

**Best practice:** Only remove fields that contain truly sensitive information (e.g., `affected_components` with internal IP addresses). Be selective to ensure the LLM has enough context to provide meaningful assistance.

**How it works:** When a tool or resource returns data, the FieldExcluder removes the specified fields from the data structure before sending it to the LLM. On write operations (create/update), the LLM's data is sent directly without restoration, since the excluded fields are not part of the conversation context.
