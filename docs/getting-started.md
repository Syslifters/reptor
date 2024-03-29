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
```
--8<-- "docs/cli/help-messages/reptor"
```
