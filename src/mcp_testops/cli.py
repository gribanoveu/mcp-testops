"""``python -m mcp_testops call ...`` — one tool from the shell, no MCP client needed.

The server speaks stdio only, so this starts it the way a client does (one subprocess),
performs a single call and prints the answer the model would see::

    call --list                 one line per tool
    call --schema <tool>        the argument schema
    call <tool> '<json>'        the call itself, arguments as a JSON object

Exit code: 0 when the tool answered, 1 when the protocol reported an error or the
arguments are not JSON. A tool that answers ``{"ok": false, "error": ...}`` is still an
answer — our tools report failures as data, so read the field.
"""

from __future__ import annotations

import json
import os
import sys

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import TOKEN, TOKEN_HINT


def _self_command() -> tuple[str, list[str]]:
    """How to start this very package as a server: a frozen binary is its own executable."""
    if getattr(sys, "frozen", False):
        return sys.executable, []
    return sys.executable, ["-m", "mcp_testops"]


async def _run(argv: list[str]) -> int:
    command, args = _self_command()
    params = StdioServerParameters(command=command, args=args, env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if argv[0] == "--list":
                for tool in (await session.list_tools()).tools:
                    first = tool.description.splitlines()[0] if tool.description else ""
                    print(f"{tool.name}\t{first}")
                return 0

            if argv[0] == "--schema":
                tools = {tool.name: tool for tool in (await session.list_tools()).tools}
                name = argv[1] if len(argv) > 1 else ""
                if name not in tools:
                    print(f"no such tool: {name or '(none)'}", file=sys.stderr)
                    return 1
                print(json.dumps(tools[name].input_schema, ensure_ascii=False, indent=2))
                return 0

            try:
                arguments = json.loads(argv[1]) if len(argv) > 1 else {}
            except json.JSONDecodeError as error:
                print(f"arguments are not JSON: {error}", file=sys.stderr)
                return 1
            result = await session.call_tool(argv[0], arguments)
            print(result.content[0].text if result.content else "")
            return 1 if result.is_error else 0


def run_call(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if not TOKEN:
        print(TOKEN_HINT, file=sys.stderr)
        print("Per command, without exporting: TESTOPS_TOKEN=... python -m mcp_testops call --list", file=sys.stderr)
        return 1
    # anyio.run, not asyncio.run: the stdio transport of the SDK builds its transport with
    # anyio task groups, and under asyncio.run their teardown raises an ExceptionGroup after
    # the answer has already been printed (Python 3.14, anyio 4).
    return anyio.run(_run, argv)
