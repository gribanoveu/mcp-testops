"""MCP server for Allure TestOps.

Transport is stdio; everything that depends on the stand and the project comes
from ``TESTOPS_*`` environment variables (see README).

Layout: ``config`` reads the environment, ``client`` talks to the stand,
``helpers`` and ``bodies`` hold the shared pieces, ``server`` owns the
``MCPServer`` object, ``tools`` registers one function per tool.
"""

from .bodies import (
    _bulk_run_body,
    _launch_body,
    _patch_body,
    _step_body,
    _test_case_body,
    _test_plan_body,
    _test_result_body,
)
from .client import TestOpsError, _api, _configure_logging, _http, _paged
from .config import TOKEN
from .server import mcp
from .tools.launches import (
    add_test_result,
    close_launch,
    create_launch,
    delete_launch,
    get_launch,
    get_launch_statistic,
    get_test_result,
    list_launches,
    list_test_results,
    reopen_launch,
    run_test_cases,
)
from .tools.projects import get_project, list_projects
from .tools.references import list_reference, list_statuses
from .tools.cases import (
    add_test_case_step,
    create_test_case,
    delete_test_case,
    get_test_case,
    get_test_case_history,
    get_test_case_steps,
    list_test_cases,
    search_test_cases,
    update_test_case,
    validate_aql,
)
from .tools.plans import (
    create_test_plan,
    delete_test_plan,
    get_test_plan,
    list_test_plans,
    update_test_plan,
)

__all__ = [
    "TestOpsError",
    "mcp",
    "main",
    "add_test_case_step",
    "add_test_result",
    "close_launch",
    "create_launch",
    "create_test_case",
    "create_test_plan",
    "delete_launch",
    "delete_test_case",
    "delete_test_plan",
    "get_launch",
    "get_launch_statistic",
    "get_project",
    "get_test_case",
    "get_test_case_history",
    "get_test_case_steps",
    "get_test_plan",
    "get_test_result",
    "list_launches",
    "list_projects",
    "list_reference",
    "list_statuses",
    "list_test_cases",
    "list_test_plans",
    "list_test_results",
    "reopen_launch",
    "run_test_cases",
    "search_test_cases",
    "update_test_case",
    "update_test_plan",
    "validate_aql",
]


def main() -> None:
    """Run the stdio server; refuses to start without a token."""
    if not TOKEN:
        raise SystemExit("TESTOPS_TOKEN is not set")
    _configure_logging()
    mcp.run()
