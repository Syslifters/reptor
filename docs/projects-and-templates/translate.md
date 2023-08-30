# Translate

## Usage

```
--8<-- "docs/cli/assets/help-messages/translate"
```

## Sample commands

```
python3 -m reptor translate -to DE --dry-run
python3 -m reptor translate --from EN -to DE
python3 -m reptor translate -to DE --skip-fields recommendation,summary --dry-run
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