# reptor (alpha version)
reptor allows you to automate pentest reporting with SysReptor.

 * Create findings and notes from tool outputs
 * Upload evidences (also bulk upload)
 * Import data from other reporting tools

**GitHub:** [https://github.com/Syslifters/reptor/](https://github.com/Syslifters/reptor/){ target=_blank }  
**Docs:** [https://docs.sysreptor.com/cli/getting-started](https://docs.sysreptor.com/cli/getting-started){ target=_blank }   
**Setup:** [https://docs.sysreptor.com/cli/setup](https://docs.sysreptor.com/cli/setup){ target=_blank }   
**PyPi:** [https://pypi.org/project/reptor/](https://pypi.org/project/reptor/){ target=_blank }   


## Usage

```usage: reptor [-h] [-s SERVER] [-t TOKEN] [-k] [-p PROJECT_ID]
              [--personal-note] [-f] [-v] [--debug] [-n NOTENAME] [-nt]
              [-file FILE]

Examples:
                reptor conf
                echo "Upload this!" | reptor note
                reptor file data/*
                cat sslyze.json | reptor sslyze --json --push-findings
                cat nmap.xml | reptor nmap --xml --upload --multi-notes

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity (> INFO)
  --debug               sets logging to DEBUG
  -n NOTENAME, --notename NOTENAME
  -nt, --no-timestamp   do not prepent timestamp to note
  -file FILE, --file FILE
                        Local file to read

subcommands:
  
  configuration:
  conf                  Shows config and sets config
  
  uploads:
  finding               Uploads findings from JSON or TOML
  file                  Uploads a file
  note                  Uploads and lists notes
  
  tools:
  sslyze                format sslyze JSON output
  nmap                  format nmap output
  zap                   Parses ZAP reports (JSON, XML)
  nikto                 Formats Nikto output (XML)
  
  importers:
  ghostwriter           Imports GhostWriter finding templates
  
  other:
  importers             Show importers to use to import finding templates
  plugins               Allows plugin management & development
  project               Work with projects
  translate             Translate Projects to other languages via Deepl
  template              Queries Finding Templates from reptor.api

configuration:
  -s SERVER, --server SERVER
  -t TOKEN, --token TOKEN
                        SysReptor API token
  -k, --insecure        do not verify server certificate
  -p PROJECT_ID, --project-id PROJECT_ID
                        SysReptor project ID
  --personal-note       add notes to private notes
  -f, --force-unlock    force unlock notes

```