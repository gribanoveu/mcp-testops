"""Client behaviour against a mocked stand: pagination, oneOf launches, 202/204, errors, retries."""

import json

import httpx
import pytest

import mcp_testops as testops

PREVIEW_PAGE = {
    "content": [
        {
            "id": 1,
            "name": "Regress",
            "projectId": 65,
            "closed": False,
            "createdDate": 1762600000000,
            "newDefectsCount": 2,
            "knownDefectsCount": 1,
            "statistic": [{"count": 3, "status": "passed"}, {"count": 1, "status": "failed"}],
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "number": 0,
    "size": 50,
    "numberOfElements": 1,
    "first": True,
    "last": True,
    "empty": False,
}

LAUNCH_PAGE = {
    "content": [
        {
            "id": 2,
            "name": "Release 1.0",
            "projectId": 65,
            "closed": True,
            "createdDate": 1762600000000,
            "autoclose": True,
            "releaseId": 4,
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "number": 0,
    "size": 50,
}


def test_paged_reads_envelope_and_meta(api):
    seen = {}

    def handler(request):
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json=PREVIEW_PAGE)

    api(handler)
    res = testops._paged("/api/testcase", {"projectId": 65})
    assert res == {
        "content": PREVIEW_PAGE["content"],
        "totalElements": 1,
        "totalPages": 1,
        "number": 0,
        "size": 50,
    }
    assert seen["query"]["page"] == "0" and seen["query"]["size"] == "50"
    assert seen["query"]["projectId"] == "65"


def test_paged_caps_size_at_100(api):
    seen = {}

    def handler(request):
        seen["size"] = request.url.params["size"]
        return httpx.Response(200, json=PREVIEW_PAGE)

    api(handler)
    testops.list_test_cases(project_id=65, size=1000)
    assert seen["size"] == "100"


def test_list_launches_reads_preview_shape(api):
    api(lambda request: httpx.Response(200, json=PREVIEW_PAGE))
    answer = json.loads(testops.list_launches(project_id=65))
    assert answer["ok"] is True
    assert answer["content"] == [
        {"id": 1, "name": "Regress", "closed": False, "createdDate": 1762600000000,
         "statistic": {"passed": 3, "failed": 1}}
    ]


def test_list_launches_reads_launch_shape(api):
    api(lambda request: httpx.Response(200, json=LAUNCH_PAGE))
    answer = json.loads(testops.list_launches(project_id=65))
    assert answer["content"][0]["closed"] is True
    assert answer["content"][0]["statistic"] == {}


def test_202_is_accepted(api):
    api(lambda request: httpx.Response(202))
    assert testops._api("DELETE", "/api/testcase/1") == {"ok": True, "accepted": True}


def test_204_is_accepted(api):
    api(lambda request: httpx.Response(204))
    assert testops._api("DELETE", "/api/launch/2") == {"ok": True, "accepted": True}


def test_error_carries_server_message(api):
    api(lambda request: httpx.Response(404, json={"message": "test case not found"}))
    answer = json.loads(testops.get_test_case(1))
    assert answer == {"ok": False, "error": "HTTP 404 on GET /api/testcase/1: test case not found"}


def test_non_json_success_is_an_error(api):
    api(lambda request: httpx.Response(200, text="<html>proxy</html>"))
    answer = json.loads(testops.get_test_case(1))
    assert answer["ok"] is False
    assert "non-JSON response" in answer["error"]


def test_get_retries_server_error(api, monkeypatch):
    monkeypatch.setattr(testops, "RETRY_BACKOFF", 0)
    calls = []

    def handler(request):
        calls.append(request.method)
        if len(calls) == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"id": 65, "isPublic": True, "isVersioned": True, "name": "P"})

    api(handler)
    answer = json.loads(testops.get_project(65))
    assert answer["ok"] is True
    assert len(calls) == 2


def test_post_is_not_retried(api, monkeypatch):
    monkeypatch.setattr(testops, "RETRY_BACKOFF", 0)
    calls = []

    def handler(request):
        calls.append(request.method)
        return httpx.Response(500, json={"message": "boom"})

    api(handler)
    answer = json.loads(testops.create_test_case(name="Case", project_id=65))
    assert answer == {"ok": False, "error": "HTTP 500 on POST /api/testcase: boom"}
    assert len(calls) == 1


def test_get_test_case_steps_builds_tree(api):
    scenario = {
        "root": {"id": 0, "children": [1, 2]},
        "scenarioSteps": {
            "1": {"id": 1, "body": "Open the form", "children": [3]},
            "2": {"id": 2, "body": "Close the form", "children": []},
            "3": {"id": 3, "body": "Fill the login", "expectedResult": "field is filled"},
        },
    }
    api(lambda request: httpx.Response(200, json=scenario))
    answer = json.loads(testops.get_test_case_steps(42))
    steps = answer["steps"][0]["children"]
    assert [step["id"] for step in steps] == [1, 2]
    assert steps[0]["children"] == [
        {"id": 3, "body": "Fill the login", "expectedResult": "field is filled", "children": []}
    ]


def test_get_test_case_steps_raw_form(api):
    scenario = {"scenarioSteps": {"1": {"id": 1, "body": "Step"}}}
    api(lambda request: httpx.Response(200, json=scenario))
    answer = json.loads(testops.get_test_case_steps(42, as_tree=False))
    assert answer == {"ok": True, "testCaseId": 42, "scenarioSteps": scenario["scenarioSteps"]}


def test_search_by_name_builds_aql(api):
    seen = {}

    def handler(request):
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0, "size": 50})

    api(handler)
    answer = json.loads(testops.search_test_cases(project_id=65, name="login"))
    assert answer["rql"] == 'name ~ "login"'
    assert seen["query"]["rql"] == 'name ~ "login"'
    assert "page" in seen["query"]


def test_search_without_query_is_an_error(api):
    api(lambda request: pytest.fail("no request expected"))
    answer = json.loads(testops.search_test_cases(project_id=65))
    assert answer == {"ok": False, "error": "rql or name is required"}
