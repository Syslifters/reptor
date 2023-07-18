# SysReptor CLI "reptor"
Description

# Table of Contents
- [SysReptor CLI "reptor"](#sysreptor-cli-reptor)
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [How to use](#how-to-use)
  - [Config](#config)
  - [Upload notes](#upload-notes)
  - [Upload files](#upload-files)
  - [Custom Plugins](#custom-plugins)
    - [nmap](#nmap)
    - [sslyze](#sslyze)
  - [Community Plugins](#community-plugins)
  - [Private Plugins](#private-plugins)
- [How to contribute](#how-to-contribute)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
- [License](#license)



# Installation

```
pip install reptor
```

We follow the Django release/requirement cycle. This means, that we support up to the lowest version that django supports.

We recommend to install reptor in a virtualenvironment to make sure that the dependencies to not clash with your current system. Simply follow the instructions:

```
virtualenv .venv
./.venv/bin/activate
pip install reptor
```

or with pyenv:
```
# pyenv global 3.11.3
pyenv virtualenv reptor
pyenv local reptor
pip install reptor
```

# How to use

```
❯ python -m reptor --help
usage: reptor [-h] [-s SERVER] [-t TOKEN] [-f] [--insecure] [-p PROJECT_ID | --private-note] [-v] [--debug] [-n NOTENAME] [-nt] [-file FILE]

Examples:
                python -m reptor projects --search "matrix"
                python -m reptor nikto --xml --file ./nikto_results.xml

options:
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

  upload:
  file                  Uploads a file
  note                  Uploads a note

  tool output processing:
  nmap
  sslyze                format sslyze JSON output
  owaspzap              Parses OWASPZap XML and JSON reports
  nikto                 Formats Nikto output (Raw, XML, JSON)
  simplelist            format list output

  other:
  importers             Show importers to use to import finding templates
  projects              Queries Projects from reptor.api
  plugins               Allows plugin management & development
  notes                 Lists current notes
  templates             Queries Finding Templates from reptor.api
  translate             Translate Projects and Templates to other languages

  finding templates importers:
  ghostwriter

configuration:
  -s SERVER, --server SERVER
  -t TOKEN, --token TOKEN
                        SysReptor API token
  -f, --force-unlock    force unlock notes and sections
  --insecure            do not verify server certificate
  -p PROJECT_ID, --project-id PROJECT_ID
                        SysReptor project ID
  --private-note        add notes to private notes

```


## Config
```
$ python3 reptor conf
Server [https://demo.sysre.pt]:
Session ID: fegk1dii32cft9rvi3qkaz0lywos0huf
Project ID: 52822d8c-947a-47bf-bc80-b7aebbc70e84
Store to config file to ~/.sysreptor/config.yaml? [y/n]: y
```

## Upload notes
```
$ echo "Upload this!" | python3 reptor note
Reading from stdin...
Note written to "Uploads".
```

```
$ echo "Upload this!" | python3 reptor note --notename "Test"
Reading from stdin...
Note written to "Test".
```

## Upload files
```
$ python3 reptor file test_data/*
```

```
$ cat img.png | python3 reptor file --filename file.png
```

## Custom Plugins
### nmap

```
$ cat test_data/nmap_output.txt | python3 reptor nmap
Reading from stdin...
| Host | Port | Service | Version |
| ------- | ------- | ------- | ------- |
| 127.0.0.1 | 80/tcp | http | n/a |
| 127.0.0.1 | 443/tcp | ssl/http | n/a |
```

```
$ cat test_data/nmap_output.txt | python3 reptor nmap -upload
```

### sslyze
```
$ cat test_data/sslyze.txt | python3 reptor nmap
```

```
$ cat test_data/sslyze.txt | python3 reptor nmap -upload
```

## Community Plugins
Check out the community contributions in `plugins/community` to find if your current tool is supported.

You can also create a plugin for a new tool or extend existing plugins. Simply create a Pull Request and add your plugin.
## Private Plugins
To install new plugins, that are not included in the community folder of this repository you can simply
put them into your home directory:
```
~/.sysreptor/plugins/PLUGINNAME
```


# How to contribute

To start a new plugin yourself you can use the `plugins` plugin.
```
reptor plugins --new "MyPlugin"
```

This will create a new plugin call "MyPlugin" within your home directory's `.sysreptor/plugins` folder.

You can lean more about how to write a plugin via the documentation here.

You can also write an Importer to import finding templates. Use the importer plugin the same way:

```
reptor importers --new "MyImporter"
```

[Contributors](CONTRIBUTING.md)

# Testing
## Unit Tests

```
make test
```

or specific

```
python -m unittest discover -v -s reptor/plugins/core/Nmap
```

# License

[LICENSE](LICENSE)

[NOTICE](NOTICE)