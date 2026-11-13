"""Configuration from the environment: one package, many stands."""

import os


SERVER_NAME = os.getenv("MCP_SERVER_NAME", "testops")
BASE_URL = os.getenv("TESTOPS_BASE_URL", "https://testops.net").rstrip("/")
TOKEN = os.getenv("TESTOPS_TOKEN")
DEFAULT_PROJECT_ID = os.getenv("TESTOPS_PROJECT_ID")
TIMEOUT = float(os.getenv("TESTOPS_TIMEOUT", "60"))


def _flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


VERIFY_SSL = _flag("TESTOPS_VERIFY_SSL")
READ_ONLY = _flag("TESTOPS_READ_ONLY")

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
RETRY_STATUSES = {429, 500, 502, 503, 504}
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 0.5

TEST_STATUSES = ("failed", "broken", "passed", "skipped", "unknown", "in_progress")
REFERENCE_KINDS = ("workflow", "testlayer", "custom_field", "tag")

# What to print when the token is missing: the same lines serve the stdio server, where a
# client reads them in its log, and the CLI, where the user reads them in the terminal.
# The shell syntax is not the same everywhere — `export` means nothing to cmd.exe or PowerShell,
# and those are the two shells most of the Windows users of this package have.
def token_hint() -> str:
    lines = [
        "TESTOPS_TOKEN is not set: the token goes to the stand as `Authorization: Api-Token <token>`.",
    ]
    if os.name == "nt":
        lines += [
            '  $env:TESTOPS_TOKEN = "<api token>"                # PowerShell; never commit it',
            "  set TESTOPS_TOKEN=<api token>                     # cmd.exe",
            '  $env:TESTOPS_BASE_URL = "https://testops.net"     # optional, this is the default',
            '  $env:TESTOPS_PROJECT_ID = "<id>"                  # optional, for tools called without project_id',
        ]
    else:
        lines += [
            "  export TESTOPS_TOKEN=<api token>                   # from your TestOps profile; never commit it",
            "  export TESTOPS_BASE_URL=https://testops.net        # optional, this is the default",
            "  export TESTOPS_PROJECT_ID=<id>                     # optional, for tools called without project_id",
            "  export TESTOPS_VERIFY_SSL=true                     # optional, on a stand with a valid certificate",
        ]
    return "\n".join(lines)


def token_one_liner() -> str:
    """How to pass the token to one command, in the syntax of this platform's shell."""
    if os.name == "nt":
        return 'Per command (PowerShell): $env:TESTOPS_TOKEN="<api token>"; python -m mcp_testops call --list'
    return "Per command: TESTOPS_TOKEN=<api token> python -m mcp_testops call --list"
