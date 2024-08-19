# Prerequisites

* Python 3.9-3.12
* pip3

# Installation
## From pypi
`pip3 install reptor`

### Optional dependencies
* translate (requires deepl)
* ghostwriter (requires gql)
* dev (requires pytest)

Install by `pip3 install reptor[translate]`.  
Install all optional dependencies using `pip3 install reptor[all]`

## From source
```
git clone https://github.com/Syslifters/reptor.git
cd reptor
pip3 install .
```

Install [optional dependencies](#optional-dependencies) by `pip3 install .[all]`.