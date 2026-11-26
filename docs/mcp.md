# MCP

`reptor mcp` starts a Model Context Protocol server so an external agent can work with SysReptor projects, findings, finding templates, report sections, and notes.

It uses the same server, API token, and project as the rest of the CLI. Configure them with `reptor conf`, the environment variables `REPTOR_SERVER`, `REPTOR_TOKEN`, and `REPTOR_PROJECT_ID`, or the flags `-s`, `-t`, and `-p`. See [Configuration](/cli/configuration).

The in-app SysReptor assistant is documented at [AI Agent](/reporting/ai-agent).

## Examples
```shell
reptor mcp
reptor mcp --read-only
reptor mcp --transport streamable-http
reptor mcp --transport streamable-http --host 0.0.0.0
reptor mcp --mcp-debug /tmp/reptor-mcp.log
```

::: warning
The HTTP transports bind to `127.0.0.1` by default. `--host 0.0.0.0` listens on every interface. Anyone who can reach the port can use the API token with the same permissions the token has. Prefer stdio, or `--read-only`, when the client should not change report data.
:::


## Installation
Make sure you installed required dependencies by using `pipx inject --force reptor 'reptor[mcp]'` or `pipx inject --force reptor 'reptor[all]'`.

## Start the server
The default transport is stdio. Local clients spawn `reptor mcp` and talk to it over stdin and stdout.

```shell
reptor mcp
reptor mcp --read-only
```

For remote access, use streamable HTTP. It listens on `127.0.0.1:8000` unless you set `--host` and `--port`. Those flags are ignored for stdio. The endpoint path is `/mcp`.

```shell
reptor mcp --transport streamable-http
reptor mcp --transport streamable-http --host 0.0.0.0
```

Clients connect to `http://127.0.0.1:8000/mcp`. With `--host 0.0.0.0` the server listens on every interface, and clients use the machine's address, for example `http://192.168.1.10:8000/mcp`.

`sse` is deprecated. Prefer `streamable-http` for remote access.

Stdio is the MCP channel, so debug logs go to a file:

```shell
reptor mcp --mcp-debug /tmp/reptor-mcp.log
```

## Client setup
Any stdio client can launch the server with command `reptor` and args `mcp`. In Cursor, add this to `mcp.json`:

```json
{
  "mcpServers": {
    "reptor": {
      "command": "reptor",
      "args": ["mcp"]
    }
  }
}
```

To withhold write tools, pass `--read-only`:

```json
{
  "mcpServers": {
    "reptor": {
      "command": "reptor",
      "args": ["mcp", "--read-only"]
    }
  }
}
```

For streamable HTTP, start the server yourself and point the client at `http://127.0.0.1:8000/mcp`.

## Project selection
Every project-scoped tool uses the one project configured at startup. To work on a different project, start the server again with that project id.

## Read-only mode
`--read-only` does not register write tools. These tools are omitted:

- `create_finding`
- `patch_finding`
- `delete_finding`
- `reptor_patch_project_data`
- `reptor_write_note`

## Field exclusion
`--remove-fields` strips fields before they are sent to the model. Use it when a field is large or irrelevant to the task and would only crowd the model's context, or when that field should not leak to the AI. Prefix a name with `finding:`, `note:`, or `section:`. A name without a prefix is a finding field.

A bare field name is removed everywhere it appears. A dotted path is removed only at that path (`finding:data.cvss`).

```shell
reptor mcp --remove-fields affected_components,note:icon_emoji,section:label
```

## Usage
<<< @/cli/help-messages/mcp{txt}
