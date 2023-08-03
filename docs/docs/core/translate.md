# Translate

## Usage
```
usage: reptor translate [-h] [-from LANGUAGE_CODE] [-to LANGUAGE_CODE] [-translator {deepl}] [-dry-run]

Translate Projects and Templates to other languages

options:
  -h, --help            show this help message and exit
  -from LANGUAGE_CODE, --from LANGUAGE_CODE
                        Language code of source language
  -to LANGUAGE_CODE, --to LANGUAGE_CODE
                        Language code of dest language
  -translator {deepl}, --translator {deepl}
                        Translator service to use
  -dry-run, --dry-run   Do not translate, count characters to be translated and checks Deepl quota
```

## Installation
Make sure you installed the correct dependency by using `pip install reptor[translate]` or `pip install reptor[all]`.

## Configuration
Run `reptor conf` to setup your initial configuration.

The translate module needs additional configurations, which you can add to `~/.sysreptor/config.yaml`:

```
translate:
  deepl_api_token: <your-api-token>
  skip_fields:
  - description
```

`skip_fields` can be used to do not translate certain report or finding fields.

## Dry run
Use 