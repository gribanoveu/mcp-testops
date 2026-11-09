"""MCP server for Allure TestOps.

Transport is stdio; everything that depends on the stand and the project comes
from ``TESTOPS_*`` environment variables (see README).
"""

import os

from mcp.server import MCPServer

SERVER_NAME = os.getenv("MCP_SERVER_NAME", "testops")
BASE_URL = os.getenv("TESTOPS_BASE_URL", "https://testops.moscow.alfaintra.net")
TOKEN = os.getenv("TESTOPS_TOKEN")
DEFAULT_PROJECT_ID = os.getenv("TESTOPS_PROJECT_ID")

mcp = MCPServer(SERVER_NAME)


def main() -> None:
    """Run the stdio server; refuses to start without a token."""
    if not TOKEN:
        raise SystemExit("TESTOPS_TOKEN is not set")
    mcp.run()
