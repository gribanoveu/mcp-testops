#!/usr/bin/env python3
"""Call one tool of the testops MCP server from the shell.

    TESTOPS_TOKEN=... python scripts/call.py list_projects '{"search": "wowtax"}'
    TESTOPS_TOKEN=... python scripts/call.py --list
    TESTOPS_TOKEN=... python scripts/call.py --schema get_test_case_steps

It starts `python -m mcp_testops` over stdio, the way a client does, so what comes back is
exactly what the model sees. The server reads TESTOPS_* from the environment, as always.

anyio.run, not asyncio.run: the stdio client of the MCP SDK builds its transport with anyio
task groups, and under asyncio.run their teardown raises an ExceptionGroup after the answer
is already printed (Python 3.14, anyio 4). Same code under anyio.run exits quietly.
"""

import json
import os
import sys

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0

    params = StdioServerParameters(
        command=sys.executable, args=["-m", "mcp_testops"], env=dict(os.environ)
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if argv[0] == "--list":
                for tool in (await session.list_tools()).tools:
                    first = tool.description.splitlines()[0] if tool.description else ""
                    print(f"{tool.name}: {first}")
                return 0

            if argv[0] == "--schema":
                tools = {tool.name: tool for tool in (await session.list_tools()).tools}
                tool = tools.get(argv[1]) if len(argv) > 1 else None
                if tool is None:
                    print(f"no such tool: {argv[1] if len(argv) > 1 else '(none)'}", file=sys.stderr)
                    return 1
                print(json.dumps(tool.input_schema, ensure_ascii=False, indent=2))
                return 0

            try:
                arguments = json.loads(argv[1]) if len(argv) > 1 else {}
            except json.JSONDecodeError as error:
                print(f"arguments are not JSON: {error}", file=sys.stderr)
                return 1
            result = await session.call_tool(argv[0], arguments)
            print(result.content[0].text if result.content else json.dumps({"ok": not result.is_error}))
            return 1 if result.is_error else 0


if __name__ == "__main__":
    raise SystemExit(anyio.run(main, sys.argv[1:]))
