"""Guards: project_id resolution, TESTOPS_READ_ONLY registration, api_request restrictions."""

import asyncio
import json

import httpx
import pytest

import mcp_testops

READ_TOOLS = [
    "api_request",
    "get_launch",
    "get_project",
    "get_test_case",
    "get_test_case_steps",
    "get_test_plan",
    "list_launches",
    "list_projects",
    "list_test_cases",
    "list_test_plans",
    "list_test_results",
    "search_test_cases",
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


def test_api_request_refuses_delete_project(fresh, api):
    module = fresh(TESTOPS_READ_ONLY=None)
    api(lambda request: "delete must not reach the stand")

    answer = json.loads(module.api_request("DELETE", "/api/project/65"))
    assert answer == {"ok": False, "error": "DELETE /api/project* is not allowed"}


def test_api_request_refuses_paths_outside_api(fresh):
    module = fresh()
    answer = json.loads(module.api_request("GET", "/testcase"))
    assert answer == {"ok": False, "error": "path must start with /api"}


def test_api_request_refuses_prefix_lookalikes(fresh):
    module = fresh()
    answer = json.loads(module.api_request("GET", "/apifoo"))
    assert answer == {"ok": False, "error": "path must start with /api"}


def test_api_request_refuses_secret_endpoints(fresh):
    module = fresh()
    for prefix in (
        "/api/account",
        "/api/register",
        "/api/admin",
        "/api/mfa",
        "/api/globalsettings/mfa",
        "/api/email-verification",
        "/api/invite",
        "/api/login/invite-personal",
        "/api/integration",
        "/api/token",
    ):
        answer = json.loads(module.api_request("GET", f"{prefix}/1"))
        assert answer["ok"] is False, f"{prefix} reached the stand"
        assert answer["error"] == f"{prefix}* endpoints are not available through api_request"


def test_api_request_normalizes_before_checking(fresh):
    module = fresh()
    # Dot segments resolve the same way on the client and on the server: the result must
    # not collapse into a forbidden path, and the encoded or dotted spellings must not
    # sneak past the deny list.
    assert module._normalized_path("/api/testcase/../api/account/1") == "/api/api/account/1"
    for path in ("/api/%61ccount/1", "/api/./account/1", "/api//account/1"):
        answer = json.loads(module.api_request("GET", path))
        assert answer["ok"] is False, f"{path} reached the stand"


def test_api_request_refuses_array_body(fresh):
    module = fresh()
    answer = json.loads(module.api_request("POST", "/api/tag", body_json="[1, 2]"))
    assert answer == {"ok": False, "error": "body_json must be a JSON object"}
    answer = json.loads(module.api_request("GET", "/api/tag", params_json="[1]"))
    assert answer == {"ok": False, "error": "params_json must be a JSON object"}


def test_api_request_refuses_unknown_method(fresh):
    module = fresh()
    answer = json.loads(module.api_request("HEAD", "/api/tag"))
    assert answer["ok"] is False
    assert answer["error"].startswith("method must be one of")


def test_api_request_allows_get_in_read_only(fresh, api):
    module = fresh(TESTOPS_READ_ONLY="true")
    api(lambda request: httpx.Response(200, json=[{"id": 1, "name": "regress"}]))
    answer = json.loads(module.api_request("GET", "/api/tag"))
    assert answer == {"ok": True, "data": [{"id": 1, "name": "regress"}]}


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_api_request_blocks_writes_in_read_only(fresh, method):
    module = fresh(TESTOPS_READ_ONLY="true")
    answer = json.loads(module.api_request(method, "/api/tag", body_json='{"name": "x"}'))
    assert answer == {"ok": False, "error": "read-only mode: only GET is allowed"}


def test_main_refuses_to_start_without_token(fresh):
    module = fresh(TESTOPS_TOKEN=None)
    with pytest.raises(SystemExit, match="TESTOPS_TOKEN is not set"):
        module.main()
