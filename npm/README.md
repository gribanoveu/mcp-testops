# @gribanoveu/mcp-testops

Run the [mcp-testops](https://github.com/gribanoveu/mcp-testops) MCP server without
installing Python: this package downloads the standalone binary for your platform from
the matching GitHub release and hands it to your MCP client over stdio.

```bash
npx -y @gribanoveu/mcp-testops          # run without installing
npm install -g @gribanoveu/mcp-testops  # or install it: the command is `mcp-testops`
```

Client configuration — the same `command`/`args`/`env` shape any local MCP server takes:

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gribanoveu/mcp-testops"],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "****"
      }
    }
  }
}
```

The binary goes to `~/.cache/mcp-testops/<version>/` on first run; later runs use it.
Platforms: darwin-arm64, linux-x64, linux-arm64, win32-x64. Intel macOS is not built (the
generated binary dies on an OpenSSL mismatch on the runner) — use `uvx mcp-testops` there.

Everything the launcher says goes to stderr — stdout is the MCP protocol.

## Configuration

Everything that depends on the stand comes from the environment. The server sees exactly the
`env` block of its client entry — variables from your shell do not reach it.

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `TESTOPS_TOKEN` | yes | — | API token of the stand; without it the server exits with `TESTOPS_TOKEN is not set` |
| `TESTOPS_BASE_URL` | no | `https://testops.net` | stand host; a trailing `/` is dropped |
| `TESTOPS_PROJECT_ID` | no | — | project used by tools called without `project_id` |
| `TESTOPS_TIMEOUT` | no | `60` | one HTTP request, in seconds |
| `TESTOPS_VERIFY_SSL` | no | `false` | verify TLS; off by default for a stand on a self-signed CA |
| `TESTOPS_READ_ONLY` | no | `false` | `true` registers the 17 read tools only, the 13 write ones disappear |
| `MCP_SERVER_NAME` | no | `testops` | the server name the client shows |

`TESTOPS_VERIFY_SSL` and `TESTOPS_READ_ONLY` take `1`, `true`, `yes` or `on` in any case; anything
else counts as off. The token is sent as `Authorization: Api-Token <token>`; if the stand answers
`401` or `403`, try `Bearer`.

Not configurable from the environment: page size (50 by default, 100 at most), retries (read
requests only, 3 attempts on 429/500/502/503/504, writes are never retried), and the log format
(method, path, status, duration — no headers, no bodies).

## Skill for an agent

The server comes with a skill that teaches a model how to use it: the map of the 30 tools, the
ready-made chains, the JSON argument shapes, the AQL reference (`aql.md` beside `SKILL.md` — fields of
test cases, results and launches, operators, epoch dates, subfields). Install it with the Skills CLI:

```bash
npx -y skills add gribanoveu/mcp-testops --skill testops-mcp
npx -y skills add gribanoveu/mcp-testops --skill testops-mcp -g   # for every project
```
