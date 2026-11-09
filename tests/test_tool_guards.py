"""Guards: project_id resolution, TESTOPS_READ_ONLY registration, api_request restrictions."""

import asyncio
import json

import httpx

import mcp_testops


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
    assert "list_test_cases" in names
    assert "get_test_case_steps" in names
    for write_tool in ("create_test_case", "update_test_case", "add_test_case_step",
                       "create_test_plan", "create_launch", "add_test_result", "run_test_cases"):
        assert write_tool not in names


def test_write_tools_are_registered_by_default(fresh):
    names = tool_names(fresh(TESTOPS_READ_ONLY=None))
    assert "create_test_case" in names
    assert "run_test_cases" in names


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
    answer = json.loads(module.api_request("GET", "/api/integration"))
    assert answer == {"ok": False, "error": "/api/integration* endpoints are not available through api_request"}


def test_api_request_refuses_array_body(fresh):
    module = fresh()
    answer = json.loads(module.api_request("POST", "/api/tag", body_json="[1, 2]"))
    assert answer == {"ok": False, "error": "body_json must be a JSON object"}


def test_api_request_allows_get_in_read_only(fresh, api):
    module = fresh(TESTOPS_READ_ONLY="true")
    api(lambda request: httpx.Response(200, json=[{"id": 1, "name": "regress"}]))
    answer = json.loads(module.api_request("GET", "/api/tag"))
    assert answer == {"ok": True, "data": [{"id": 1, "name": "regress"}]}


def test_api_request_blocks_post_in_read_only(fresh):
    module = fresh(TESTOPS_READ_ONLY="true")
    answer = json.loads(module.api_request("POST", "/api/tag", body_json='{"name": "x"}'))
    assert answer == {"ok": False, "error": "read-only mode: only GET is allowed"}
