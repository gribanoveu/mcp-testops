"""Client behaviour against a mocked stand: pagination, oneOf launches, 202/204, errors, retries."""

import json
import logging

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
    assert "statistic" not in answer["content"][0]


def test_list_launches_search_goes_through_aql(api):
    """search= on /api/launch is ignored by the stand; /api/launch/__search with rql filters."""
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0})

    api(handler)
    answer = json.loads(testops.list_launches(project_id=65, search='IDE "x"'))
    assert seen["path"] == "/api/launch/__search"
    assert seen["query"]["rql"] == 'name ~= "IDE \\"x\\""'
    assert "search" not in seen["query"]
    assert answer["rql"] == seen["query"]["rql"]


def test_list_launches_rql_wins_over_search(api):
    seen = {}

    def handler(request):
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0})

    api(handler)
    testops.list_launches(project_id=65, search="IDE", rql='tag = "smoke"')
    assert seen["query"]["rql"] == 'tag = "smoke"'


def test_list_test_plans_filters_the_page_itself(api):
    """The plan listing has no text filter: search= 400s and query= never narrows."""
    seen = {}
    page = {
        "content": [{"id": 1, "name": "Smoke plan"}, {"id": 2, "name": "Regress plan"}],
        "totalElements": 2,
        "totalPages": 1,
        "number": 0,
    }

    def handler(request):
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json=page)

    api(handler)
    answer = json.loads(testops.list_test_plans(project_id=65, search="REGRESS"))
    assert "search" not in seen["query"]
    assert [row["id"] for row in answer["content"]] == [2]
    assert answer["totalElements"] == 2


def test_add_test_result_rejects_status_without_a_request(api):
    api(lambda request: pytest.fail("invalid status must not reach the stand"))
    answer = json.loads(testops.add_test_result(launch_id=10, name="x", status="ok"))
    assert answer["ok"] is False
    assert answer["error"].startswith("status must be one of")


def test_run_test_cases_rejects_ids_with_leafs_include(api):
    api(lambda request: pytest.fail("conflicting selection must not reach the stand"))
    answer = json.loads(
        testops.run_test_cases(launch_name="Regress", project_id=65, ids="1", leafs_include="[2]")
    )
    assert answer == {"ok": False, "error": "pass either ids or leafs_include, not both"}


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
    monkeypatch.setattr(testops.client, "RETRY_BACKOFF", 0)
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
    monkeypatch.setattr(testops.client, "RETRY_BACKOFF", 0)
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
        "root": {"id": 0, "body": "Prepare", "children": [1, 2]},
        "scenarioSteps": {
            "1": {"id": 1, "body": "Open the form", "children": [3]},
            "2": {"id": 2, "body": "Close the form", "children": []},
            "3": {"id": 3, "body": "Fill the login", "expectedResult": "field is filled"},
        },
    }
    api(lambda request: httpx.Response(200, json=scenario))
    answer = json.loads(testops.get_test_case_steps(42))
    root = answer["steps"][0]
    assert root["body"] == "Prepare"
    assert [step["id"] for step in root["children"]] == [1, 2]
    assert root["children"][0]["children"] == [
        {"id": 3, "body": "Fill the login", "expectedResult": "field is filled", "children": []}
    ]


def test_get_test_case_steps_of_container_root_is_flat(api):
    """The stand's root carries only children; it must not become a step of its own."""
    scenario = {
        "root": {"children": [1, 2]},
        "scenarioSteps": {
            "1": {"id": 1, "body": "Open the form", "children": []},
            "2": {"id": 2, "body": "Close the form", "children": []},
        },
    }
    api(lambda request: httpx.Response(200, json=scenario))
    answer = json.loads(testops.get_test_case_steps(42))
    assert answer["steps"] == [
        {"id": 1, "body": "Open the form", "children": []},
        {"id": 2, "body": "Close the form", "children": []},
    ]


def test_get_test_case_steps_raw_form(api):
    scenario = {"scenarioSteps": {"1": {"id": 1, "body": "Step"}}}
    api(lambda request: httpx.Response(200, json=scenario))
    answer = json.loads(testops.get_test_case_steps(42, as_tree=False))
    assert answer == {"ok": True, "testCaseId": 42, "scenarioSteps": scenario["scenarioSteps"]}


def test_get_test_case_steps_of_empty_scenario_is_empty(api):
    """A live case without steps answers {}, and a bare {"children": []} root must not become one."""
    for payload in ({"scenarioSteps": {}, "root": {"children": []}}, {"scenarioSteps": {}}, {}):
        api(lambda request: httpx.Response(200, json=payload))
        answer = json.loads(testops.get_test_case_steps(42))
        assert answer == {"ok": True, "testCaseId": 42, "steps": []}


def test_search_by_name_builds_aql(api):
    seen = {}

    def handler(request):
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0, "size": 50})

    api(handler)
    answer = json.loads(testops.search_test_cases(project_id=65, name="login"))
    assert answer["rql"] == 'name ~= "login"'
    assert seen["query"]["rql"] == 'name ~= "login"'
    assert "page" in seen["query"]


def test_search_without_query_is_an_error(api):
    api(lambda request: pytest.fail("no request expected"))
    answer = json.loads(testops.search_test_cases(project_id=65))
    assert answer == {"ok": False, "error": "rql or name is required"}


def test_logs_method_path_and_status_only(api, caplog):
    api(lambda request: httpx.Response(200, json={"id": 65, "name": "P", "isPublic": True, "isVersioned": True}))
    with caplog.at_level(logging.INFO, logger="mcp_testops"):
        json.loads(testops.get_project(65))
    text = "\n".join(record.getMessage() for record in caplog.records)
    assert "GET /api/project/65 -> 200" in text
    assert "Api-Token" not in text and "Authorization" not in text
    assert "in " in text and "ms" in text


def test_httpx_request_log_is_silenced():
    testops._configure_logging()
    assert logging.getLogger("httpx").level == logging.WARNING


def test_delete_test_case_sends_force(api):
    seen = {}

    def handler(request):
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(202)

    api(handler)
    answer = json.loads(testops.delete_test_case(42, force=True))
    assert answer == {"ok": True, "accepted": True, "testCaseId": 42, "forced": True}
    assert seen["method"] == "DELETE"
    assert seen["path"] == "/api/testcase/42"
    assert seen["query"]["force"] == "true"


def test_update_test_plan_sends_only_passed_fields(api):
    seen = {}

    def handler(request):
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": 3, "name": "Plan", "projectId": 65})

    api(handler)
    answer = json.loads(testops.update_test_plan(3, name="Plan"))
    assert answer == {"ok": True, "id": 3, "name": "Plan", "projectId": 65}
    assert seen["method"] == "PATCH"
    assert seen["path"] == "/api/testplan/3"
    assert seen["body"] == {"name": "Plan"}


def test_delete_test_plan_is_accepted(api):
    api(lambda request: httpx.Response(204))
    assert json.loads(testops.delete_test_plan(3)) == {"ok": True, "accepted": True, "testPlanId": 3}


def test_close_and_reopen_launch(api):
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(204)

    api(handler)
    assert json.loads(testops.close_launch(4)) == {
        "ok": True, "accepted": True, "launchId": 4, "action": "closed"
    }
    assert json.loads(testops.reopen_launch(4)) == {
        "ok": True, "accepted": True, "launchId": 4, "action": "reopened"
    }
    assert seen == ["/api/launch/4/close", "/api/launch/4/reopen"]


def test_delete_launch_is_accepted(api):
    api(lambda request: httpx.Response(204))
    assert json.loads(testops.delete_launch(4)) == {"ok": True, "accepted": True, "launchId": 4}


def test_get_test_case_history_compacts_launch(api):
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(
            200,
            json={
                "content": [
                    {"id": 91, "launch": {"id": 4, "name": "Regress"}, "status": "failed",
                     "duration": 100, "createdBy": "ivanov"},
                    {"id": 92, "status": "passed"},
                ],
                "totalElements": 2,
                "totalPages": 1,
                "number": 0,
                "size": 50,
            },
        )

    api(handler)
    answer = json.loads(testops.get_test_case_history(42, project_id=65, launch_id=4))
    assert answer == {
        "ok": True,
        "projectId": 65,
        "testCaseId": 42,
        "content": [
            {"testResultId": 91, "launchId": 4, "launchName": "Regress", "status": "failed", "duration": 100},
            {"testResultId": 92, "launchId": None, "launchName": None, "status": "passed"},
        ],
        "totalElements": 2,
        "totalPages": 1,
        "number": 0,
        "size": 50,
    }
    assert seen["path"] == "/api/testcase/history"
    assert seen["query"]["testCaseId"] == "42"
    assert seen["query"]["launchId"] == "4"


def test_validate_aql_sends_query(api):
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"valid": True, "count": 7})

    api(handler)
    answer = json.loads(testops.validate_aql(project_id=65, rql='tag = "smoke"'))
    assert answer == {"ok": True, "projectId": 65, "valid": True, "count": 7}
    assert seen["path"] == "/api/testcase/query/validate"
    assert seen["query"]["projectId"] == "65"
    assert seen["query"]["rql"] == 'tag = "smoke"'


def test_validate_aql_requires_rql(api):
    api(lambda request: pytest.fail("no request expected"))
    assert json.loads(testops.validate_aql(project_id=65)) == {"ok": False, "error": "rql is required"}


def test_get_launch_statistic_counts(api):
    api(
        lambda request: httpx.Response(
            200, json=[{"status": "passed", "count": 3}, {"status": "failed", "count": 1}]
        )
    )
    answer = json.loads(testops.get_launch_statistic(4))
    assert answer == {"ok": True, "launchId": 4, "statistic": {"passed": 3, "failed": 1}}


def test_get_test_result_strips_html(api):
    api(
        lambda request: httpx.Response(
            200,
            json={
                "id": 9,
                "name": "Login",
                "status": "failed",
                "message": "boom",
                "trace": "stack",
                "description": "text",
                "descriptionHtml": "<p>text</p>",
                "preconditionHtml": "<p>pre</p>",
                "launchId": 4,
                "testCaseId": 42,
                "duration": 100,
            },
        )
    )
    answer = json.loads(testops.get_test_result(9))
    assert answer == {
        "ok": True,
        "id": 9,
        "name": "Login",
        "status": "failed",
        "message": "boom",
        "trace": "stack",
        "description": "text",
        "launchId": 4,
        "testCaseId": 42,
        "duration": 100,
    }


def test_search_escapes_quotes_in_name(api):
    seen = {}

    def handler(request):
        seen["rql"] = request.url.params["rql"]
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0, "size": 50})

    api(handler)
    testops.search_test_cases(project_id=65, name='a" or 1=1')
    assert seen["rql"] == 'name ~= "a\\" or 1=1"'


def test_http_builds_one_configured_client(monkeypatch):
    monkeypatch.setattr(testops.client, "_client", None)
    monkeypatch.setattr(testops.client, "BASE_URL", "https://stand.local")
    monkeypatch.setattr(testops.client, "TIMEOUT", 12.0)
    first = testops._http()
    second = testops._http()
    assert first is second
    assert str(first.base_url).rstrip("/") == "https://stand.local"
    assert first.headers["Authorization"].startswith("Api-Token")
    assert first.timeout.connect == 12.0


def test_create_test_case_sends_exact_body(api):
    seen = {}

    def handler(request):
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": 42, "name": "Case", "projectId": 65, "hash": "x"})

    api(handler)
    answer = json.loads(
        testops.create_test_case(
            name="Case", project_id=65, status_id=5, tags_json='[{"id": 3, "name": "smoke"}]'
        )
    )
    assert answer == {"ok": True, "id": 42, "name": "Case", "projectId": 65}
    assert seen["method"] == "POST"
    assert seen["path"] == "/api/testcase"
    assert seen["body"] == {
        "projectId": 65,
        "name": "Case",
        "statusId": 5,
        "tags": [{"id": 3, "name": "smoke"}],
    }


def test_run_test_cases_sends_leafs_include(api):
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"id": 77, "name": "Regress", "projectId": 65})

    api(handler)
    answer = json.loads(testops.run_test_cases(launch_name="Regress", project_id=65, ids="1001,1002"))
    assert answer == {"ok": True, "launchId": 77, "name": "Regress", "projectId": 65}
    assert seen["path"] == "/api/testcase/bulk/run/new"
    assert seen["body"] == {
        "launchName": "Regress",
        "selection": {"projectId": 65, "leafsInclude": [1001, 1002]},
    }


def test_202_with_body_keeps_the_payload(api):
    api(lambda request: httpx.Response(202, json={"id": 77, "name": "Regress"}))
    answer = json.loads(testops.run_test_cases(launch_name="Regress", project_id=65, ids="1"))
    assert answer == {"ok": True, "accepted": True, "launchId": 77, "name": "Regress"}


def test_add_test_case_step_returns_created_id(api):
    api(
        lambda request: httpx.Response(
            200, json={"createdStepId": 9, "scenario": {"scenarioSteps": {"1": {}, "2": {}}}}
        )
    )
    answer = json.loads(testops.add_test_case_step(test_case_id=42, body="Open the form"))
    assert answer == {"ok": True, "createdStepId": 9, "steps_count": 2}


def test_transport_error_becomes_data(api):
    def handler(request):
        raise httpx.ConnectError("connection refused", request=request)

    api(handler)
    answer = json.loads(testops.get_project(65))
    assert answer["ok"] is False
    assert "ConnectError" in answer["error"]


def test_get_gives_up_after_three_attempts(api, monkeypatch):
    monkeypatch.setattr(testops.client, "RETRY_BACKOFF", 0)
    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(503, json={"message": "maintenance"})

    api(handler)
    answer = json.loads(testops.get_project(65))
    assert answer == {"ok": False, "error": "HTTP 503 on GET /api/project/65: maintenance"}
    assert calls == ["/api/project/65"] * 3


def test_paged_rejects_non_envelope(api):
    api(lambda request: httpx.Response(200, json=[{"id": 1}]))
    answer = json.loads(testops.list_test_cases(project_id=65))
    assert answer["ok"] is False
    assert "unexpected paged response" in answer["error"]


def test_get_test_case_returns_whitelist_and_flag(api):
    api(
        lambda request: httpx.Response(
            200,
            json={
                "id": 42,
                "name": "Case",
                "description": "text",
                "descriptionHtml": "<p>text</p>",
                "preconditionHtml": "<p>pre</p>",
                "hash": "abc",
                "editable": True,
            },
        )
    )
    answer = json.loads(testops.get_test_case(42))
    assert answer == {"ok": True, "id": 42, "name": "Case", "description": "text", "steps_not_included": True}


def test_statistic_dict_form_keeps_its_keys(api):
    page = {
        "content": [
            {
                "id": 3,
                "name": "Launch",
                "projectId": 65,
                "closed": False,
                "statistic": {"passed": 3, "inProgress": 1, "total": 4},
            }
        ],
        "totalElements": 1,
        "totalPages": 1,
        "number": 0,
        "size": 50,
    }
    api(lambda request: httpx.Response(200, json=page))
    answer = json.loads(testops.list_launches(project_id=65))
    assert answer["content"][0]["statistic"] == {"passed": 3, "inProgress": 1, "total": 4}


def test_list_projects_sends_query_and_sort(api):
    """The stand filters projects by query=; its own search= is ignored and 400s on Cyrillic."""
    seen = {}

    def handler(request):
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0, "size": 50})

    api(handler)
    testops.list_projects(search="ops", favorite=True)
    assert seen["query"]["query"] == "ops"
    assert "search" not in seen["query"]
    assert seen["query"]["favorite"] == "true"
    assert seen["query"]["sort"] == "name,ASC"


def test_list_statuses_reads_workflow_and_compacts(api):
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(
            200,
            json={
                "content": [{"id": 5, "name": "Draft", "color": "#ccc", "createdBy": "ivanov"}],
                "totalElements": 1,
                "totalPages": 1,
                "number": 0,
                "size": 50,
            },
        )

    api(handler)
    answer = json.loads(testops.list_statuses(workflow_id=2))
    assert seen["path"] == "/api/status"
    assert seen["query"]["workflowId"] == "2"
    assert answer["content"] == [{"id": 5, "name": "Draft", "color": "#ccc"}]


def test_list_reference_workflow_and_testlayer(api):
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(
            200,
            json={"content": [{"id": 2, "name": "Default", "createdBy": "ivanov"}],
                  "totalElements": 1, "totalPages": 1, "number": 0, "size": 50},
        )

    api(handler)
    assert json.loads(testops.list_reference("workflow"))["content"] == [{"id": 2, "name": "Default"}]
    assert json.loads(testops.list_reference("testlayer"))["kind"] == "testlayer"
    assert seen == ["/api/workflow", "/api/testlayer"]


def test_list_reference_custom_field_is_project_scoped(api):
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(
            200,
            json={"content": [{"id": 12, "name": "Severity", "locked": False}],
                  "totalElements": 1, "totalPages": 1, "number": 0, "size": 50},
        )

    api(handler)
    answer = json.loads(testops.list_reference("custom_field", project_id=65, query="Sev"))
    assert seen["path"] == "/api/project/65/cf"
    assert seen["query"]["query"] == "Sev"
    assert answer["content"] == [{"id": 12, "name": "Severity"}]


def test_list_reference_tag_asks_the_server_to_filter(api):
    """The whole tag dictionary is 224k entries; /api/tag/suggest filters and pages it."""
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["query"] = dict(request.url.params)
        return httpx.Response(200, json={"content": [{"id": 3, "name": "smoke", "extra": 1}], "last": True})

    api(handler)
    answer = json.loads(testops.list_reference("tag", query="smoke", page=0, size=5))
    assert seen["path"] == "/api/tag/suggest"
    assert seen["query"]["query"] == "smoke"
    assert seen["query"]["size"] == "5"
    assert answer["content"] == [{"id": 3, "name": "smoke"}]


def test_list_reference_rejects_unknown_kind(api):
    api(lambda request: pytest.fail("unknown kind must not reach the stand"))
    answer = json.loads(testops.list_reference("status"))
    assert answer == {"ok": False, "error": "kind must be one of workflow, testlayer, custom_field, tag"}


def test_get_test_plan_keeps_selection(api):
    plan = {
        "id": 3,
        "name": "Plan",
        "projectId": 65,
        "baseRql": 'tag.name = "smoke"',
        "testCasesCount": 7,
        "treeSelection": {"leafsInclude": [1]},
    }
    api(lambda request: httpx.Response(200, json=plan))
    assert json.loads(testops.get_test_plan(3)) == {"ok": True, **plan}


@pytest.mark.parametrize(
    "call, path",
    [
        (lambda: testops.list_projects(), "/api/project"),
        (lambda: testops.list_test_plans(project_id=65), "/api/testplan"),
        (lambda: testops.list_test_results(launch_id=4), "/api/testresult"),
        (lambda: testops.list_launches(project_id=65), "/api/launch"),
    ],
    ids=["projects", "test_plans", "test_results", "launches"],
)
def test_list_tools_hit_their_endpoint(api, call, path):
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        return httpx.Response(200, json={"content": [], "totalElements": 0, "totalPages": 0, "number": 0, "size": 50})

    api(handler)
    answer = json.loads(call())
    assert seen["path"] == path
    assert answer["ok"] is True
    assert answer["content"] == []
    assert answer["totalElements"] == 0 and answer["totalPages"] == 0 and answer["number"] == 0

