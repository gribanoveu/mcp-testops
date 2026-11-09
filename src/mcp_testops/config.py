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
