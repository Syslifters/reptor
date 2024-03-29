# reptor (alpha version)
reptor allows you to automate pentest reporting with SysReptor.

 * Create findings and notes from tool outputs
 * Upload evidences (also bulk upload)
 * Import data from other reporting tools

**GitHub:** [https://github.com/Syslifters/reptor/](https://github.com/Syslifters/reptor/)  
**Docs:** [https://docs.sysreptor.com/cli/getting-started](https://docs.sysreptor.com/cli/getting-started)   
**Setup:** [https://docs.sysreptor.com/cli/setup](https://docs.sysreptor.com/cli/setup)   
**PyPi:** [https://pypi.org/project/reptor/](https://pypi.org/project/reptor/)   

## Prerequisites

* Python 3.8-3.11
* pip3

## Installation
### From pypi
`pip3 install reptor`

#### Optional dependencies
* translate (requires deepl)
* ghostwriter (requires gql)
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
              [--private-note] [-v] [--debug] [-n NOTETITLE] [--no-timestamp]
              [--file FILE]

Examples:
                reptor conf
                echo "Upload this!" | reptor note
                reptor file data/*
                cat sslyze.json | reptor sslyze --json --push-findings
                cat nmap.xml | reptor nmap --xml --upload

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
   plugins               Allows plugin management & development
  
  Projects & Templates:
   createproject         Create a new pentest project
   deletefindings        Deletes findings by title
   deleteprojects        Deletes projects by title
   exportfindings        Export your project findings as a summary or checklist
   file                  Uploads a file
   finding               Uploads findings from JSON or TOML
   note                  Uploads and lists notes
   project               Work with projects
   pushproject           Push data to project from JSON or TOML
   template              Queries Finding Templates from SysReptor
   translate             Translate Projects to other languages via Deepl
  
  Tools:
   nessus                Nessus vulnerability importer
   nmap                  format nmap output
   openvas               OpenVAS vulnerability importer
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
  --private-note        add notes to private notes

```