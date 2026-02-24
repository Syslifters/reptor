Translate pentest reports using DeepL or Azure OpenAI (bring your own API credentials).

## Examples
```
reptor translate --service deepl --to DE --dry-run
reptor translate --service deepl --from EN --to DE
reptor translate --service azure --to DE --skip-fields recommendation,summary
```

## Installation
Make sure you installed required dependencies by using `pip install reptor[translate]` or `pip install reptor[all]`.

For Azure OpenAI support, also install: `pip install openai`

## Configuration
The translate module needs additional configurations, which you can add to `~/.sysreptor/config.yaml`:

### DeepL Configuration
```
translate:
  service: deepl
  deepl_api_token: <your-deepl-api-token>
  skip_fields:
  - description
```

### Azure OpenAI Configuration
```
translate:
  service: azure
  azure_api_key: <your-azure-api-key>
  azure_resource_name: <your-azure-resource-name>
  azure_api_version: 2024-02-15-preview
  azure_endpoint: https://<your-resource>.openai.azure.com/
  azure_model: gpt-4
  skip_fields:
  - description
```

`skip_fields` can be used to skip translation of certain report or finding fields.


## Usage
```
--8<-- "docs/cli/help-messages/translate"
```
