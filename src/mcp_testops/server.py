"""The MCP server object and the decorator that keeps write tools out of read-only mode."""

from mcp.server import MCPServer

from .config import READ_ONLY, SERVER_NAME
from .helpers import _guard


mcp = MCPServer(SERVER_NAME)


def _write(fn):
    """Register a mutating tool only when TESTOPS_READ_ONLY is off."""
    return _guard(fn) if READ_ONLY else mcp.tool()(_guard(fn))
