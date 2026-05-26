# Ghostwriter

Migrates finding templates from Ghostwriter to SysReptor.

## Examples

```shell
reptor ghostwriter --url http://localhost/ghostwriter
```

## Installation
Make sure you installed required dependencies by using `pip install reptor[ghostwriter]` or `pip install reptor[all]`.

## Configuration
This module needs additional configurations, which you can add to your config file by running:

```shell
$ reptor ghostwriter --conf
Ghostwriter URL: https://localhost
Ghostwriter API key (x-hasura-admin-secret or JWT token): your-api-key
```

## Usage
<<< @/cli/help-messages/ghostwriter{txt}
