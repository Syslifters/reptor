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
```
--8<-- "docs/cli/help-messages/reptor"
```
