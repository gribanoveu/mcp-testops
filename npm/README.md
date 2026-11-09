# @gribanoveu/mcp-testops

Run the [mcp-testops](https://github.com/gribanoveu/mcp-testops) MCP server without
installing Python: this package downloads the standalone binary for your platform from
the matching GitHub release and hands it to your MCP client over stdio.

```bash
npx -y @gribanoveu/mcp-testops
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
Platforms: darwin-arm64, darwin-x64, linux-x64, linux-arm64, win32-x64.

Everything the launcher says goes to stderr — stdout is the MCP protocol.
