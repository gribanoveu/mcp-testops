"""Guards: project_id resolution, TESTOPS_READ_ONLY registration, no generic escape hatch."""

import asyncio
import json

import httpx
import pytest

import mcp_testops

READ_TOOLS = [
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
    "search_test_cases",
    "validate_aql",
]

WRITE_TOOLS = [
    "add_test_case_step",
    "add_test_result",
    "create_launch",
    "create_test_case",
    "create_test_plan",
    "run_test_cases",
    "update_test_case",
]


def tool_names(module) -> list[str]:
    return [tool.name for tool in asyncio.run(module.mcp.list_tools())]


def test_project_id_is_required_without_env(fresh):
    module = fresh(TESTOPS_PROJECT_ID=None)
    assert json.loads(module.list_test_cases()) == {
        "ok": False,
        "error": "project_id is required (or set TESTOPS_PROJECT_ID)",
    }


def test_project_id_comes_from_env(fresh, api):
    module = fresh(TESTOPS_PROJECT_ID="65")
    seen = {}

    def handler(request):
        seen["projectId"] = request.url.params["projectId"]
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0, "size": 50})

    api(handler)
    answer = json.loads(module.list_test_cases())
    assert answer["projectId"] == 65
    assert seen["projectId"] == "65"


def test_read_only_hides_write_tools(fresh):
    names = tool_names(fresh(TESTOPS_READ_ONLY="true"))
    assert sorted(names) == sorted(READ_TOOLS)


def test_write_tools_are_registered_by_default(fresh):
    names = tool_names(fresh(TESTOPS_READ_ONLY=None))
    assert sorted(names) == sorted(READ_TOOLS + WRITE_TOOLS)


def test_no_generic_escape_hatch(fresh):
    # The denial list of a generic api_request could never be complete: POST /api/register
    # was reachable through it while the spec has no /api/registration at all. Any new
    # need becomes a named tool instead.
    for read_only in ("true", "false"):
        names = tool_names(fresh(TESTOPS_READ_ONLY=read_only))
        assert "api_request" not in names


def test_main_refuses_to_start_without_token(fresh):
    module = fresh(TESTOPS_TOKEN=None)
    with pytest.raises(SystemExit, match="TESTOPS_TOKEN is not set"):
        module.main()
