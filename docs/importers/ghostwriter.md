## Examples
Migrate finding templates from Ghostwriter to SysReptor
```
reptor ghostwriter --url http://localhost/ghostwriter
```

## Installation
Make sure you installed required dependencies by using `pip install reptor[ghostwriter]` or `pip install reptor[all]`.

## Configuration
This module needs additional configurations, which you can add to `~/.sysreptor/config.yaml`:

```
ghostwriter:
  apikey: <your-api-token>
```

The variable `apikey` holds your Ghostwriter API key. This can be the API key or the Hasura Admin Secret.

## Usage
```
--8<-- "docs/cli/help-messages/ghostwriter"
```
