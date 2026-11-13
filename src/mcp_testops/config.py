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

# What to print when the token is missing: the same four lines serve the stdio server, where a
# client reads them in its log, and the CLI, where the user reads them in the terminal.
TOKEN_HINT = (
    "TESTOPS_TOKEN is not set: the token goes to the stand as `Authorization: Api-Token <token>`.\n"
    "  export TESTOPS_TOKEN=<api token>            # from your TestOps profile; never commit it\n"
    "  export TESTOPS_BASE_URL=https://testops.net  # optional, this is the default\n"
    "  export TESTOPS_PROJECT_ID=<id>              # optional, for tools called without project_id\n"
    "  export TESTOPS_VERIFY_SSL=true              # optional, on a stand with a valid certificate"
)
