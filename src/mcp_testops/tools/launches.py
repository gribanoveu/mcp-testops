"""Tools: launches and their results."""

from ..bodies import _bulk_run_body, _launch_body, _test_result_body
from ..client import TestOpsError, _api, _paged
from ..config import DEFAULT_PAGE_SIZE
from ..helpers import _answer, _guard, _ids, _json_arg, _pick, _pid, _statistic
from ..server import mcp, _write


LAUNCH_KEYS = (
    "id",
    "name",
    "projectId",
    "closed",
    "createdDate",
    "autoclose",
    "releaseId",
    "external",
    "tags",
)


@mcp.tool()
@_guard
def list_launches(
    project_id: int | None = None,
    search: str = "",
    filter_id: int | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """List launches of a project: id, name, closed, createdDate, statistic.

    statistic holds status counts as the API returns them, e.g. {passed, failed, broken,
    skipped, unknown} or StatisticDto with inProgress, pending and total; it is absent when
    the launch shape carries none. The API answers with two different launch shapes; both
    are read into this summary.
    project_id defaults to TESTOPS_PROJECT_ID; sort defaults to "created_date,DESC".
    """
    pid = _pid(project_id)
    res = _paged(
        "/api/launch",
        {"projectId": pid, "search": search or None, "filterId": filter_id},
        page=page,
        size=size,
        sort=sort,
    )
    content = []
    for item in res["content"]:
        summary = _pick(item, ("id", "name", "closed", "createdDate"))
        if "statistic" in item:
            summary["statistic"] = _statistic(item["statistic"])
        content.append(summary)
    res["content"] = content
    return {"ok": True, "projectId": pid, **res}


@mcp.tool()
@_guard
def get_launch(launch_id: int) -> str:
    """Get one launch: id, name, projectId, closed, createdDate, autoclose, releaseId, tags, links."""
    data = _api("GET", f"/api/launch/{launch_id}")
    return {"ok": True, **_pick(data, LAUNCH_KEYS + ("links", "issues"))}


@mcp.tool()
@_guard
def get_launch_statistic(launch_id: int) -> str:
    """Status counts of a launch as {passed: n, failed: n, broken: n, skipped: n, ...}.

    Cheaper than listing the results: one request instead of paging through them.
    """
    data = _api("GET", f"/api/launch/{launch_id}/statistic")
    return {"ok": True, "launchId": launch_id, "statistic": _statistic(data)}


@mcp.tool()
@_guard
def list_test_results(
    launch_id: int,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """List results of a launch: id, name, testCaseId, status, duration, message, trace, start, stop.

    status is one of failed, broken, passed, skipped, unknown, in_progress.
    """
    res = _paged("/api/testresult", {"launchId": launch_id}, page=page, size=size, sort=sort)
    res["content"] = [
        _pick(item, ("id", "name", "testCaseId", "status", "duration", "message", "trace", "start", "stop"))
        for item in res["content"]
    ]
    return {"ok": True, "launchId": launch_id, **res}


TEST_RESULT_KEYS = (
    "id",
    "name",
    "fullName",
    "launchId",
    "projectId",
    "testCaseId",
    "status",
    "duration",
    "message",
    "trace",
    "start",
    "stop",
    "description",
    "precondition",
    "postcondition",
    "expectedResult",
    "tags",
    "links",
    "assignee",
    "testedBy",
    "manual",
    "flaky",
    "createdDate",
    "lastModifiedDate",
)


@mcp.tool()
@_guard
def get_test_result(test_result_id: int) -> str:
    """Get one test result: status, duration, message, trace and the text fields.

    The *Html duplicates are dropped. For the small table of a whole launch use
    list_test_results or get_launch_statistic.
    """
    data = _api("GET", f"/api/testresult/{test_result_id}")
    return {"ok": True, **_pick(data, TEST_RESULT_KEYS)}


@_write
def create_launch(
    name: str,
    project_id: int | None = None,
    autoclose: bool | None = None,
    release_id: int | None = None,
    tags_json: str = "",
    links_json: str = "",
) -> str:
    """Create a launch and return {ok, id, name, projectId}.

    tags_json: [{"id": 3, "name": "regress"}];
    links_json: [{"name": "JIRA", "type": "issue", "url": "https://jira/browse/ABC-1"}].
    """
    pid = _pid(project_id)
    body = _launch_body(
        project_id=pid,
        name=name,
        autoclose=autoclose,
        release_id=release_id,
        tags=_json_arg(tags_json, "tags_json"),
        links=_json_arg(links_json, "links_json"),
    )
    data = _api("POST", "/api/launch", body=body)
    return _answer(data, **_pick(data, ("id", "name", "projectId")))


@_write
def close_launch(launch_id: int) -> str:
    """Close a launch; the API answers 204. Results are read-only afterwards."""
    data = _api("POST", f"/api/launch/{launch_id}/close")
    return _answer(data, launchId=launch_id, action="closed")


@_write
def reopen_launch(launch_id: int) -> str:
    """Reopen a closed launch so results can be added again; the API answers 204."""
    data = _api("POST", f"/api/launch/{launch_id}/reopen")
    return _answer(data, launchId=launch_id, action="reopened")


@_write
def delete_launch(launch_id: int) -> str:
    """Delete a launch together with all its results; the API answers 204."""
    data = _api("DELETE", f"/api/launch/{launch_id}")
    return _answer(data, launchId=launch_id)


@_write
def add_test_result(
    launch_id: int,
    name: str,
    status: str,
    test_case_id: int | None = None,
    duration: int | None = None,
    message: str = "",
    trace: str = "",
    start: int | None = None,
    stop: int | None = None,
    description: str = "",
    precondition: str = "",
    postcondition: str = "",
    expected_result: str = "",
    tags_json: str = "",
    links_json: str = "",
    custom_fields_json: str = "",
) -> str:
    """Record a test result in a launch and return {ok, id, name, launchId}.

    status must be one of failed, broken, passed, skipped, unknown, in_progress; any
    other value fails here, without a request. duration, start and stop are milliseconds
    (int64). test_case_id links the result to a test case.
    JSON-string arguments:
      tags_json          [{"id": 3, "name": "smoke"}]
      links_json         [{"name": "JIRA", "type": "issue", "url": "https://jira/browse/ABC-1"}]
      custom_fields_json [{"customField": {"id": 12, "name": "Severity"}, "name": "high"}]
    """
    body = _test_result_body(
        launch_id=launch_id,
        name=name,
        status=status,
        test_case_id=test_case_id,
        duration=duration,
        message=message or None,
        trace=trace or None,
        start=start,
        stop=stop,
        description=description or None,
        precondition=precondition or None,
        postcondition=postcondition or None,
        expected_result=expected_result or None,
        tags=_json_arg(tags_json, "tags_json"),
        links=_json_arg(links_json, "links_json"),
        custom_fields=_json_arg(custom_fields_json, "custom_fields_json"),
    )
    data = _api("POST", "/api/testresult", body=body)
    return _answer(data, **_pick(data, ("id", "name", "launchId")))


@_write
def run_test_cases(
    launch_name: str,
    project_id: int | None = None,
    leafs_include: str = "",
    ids: str = "",
    filter_id: int | None = None,
    assignees: str = "",
    tags_json: str = "",
    release_id: int | None = None,
) -> str:
    """Create a launch with one manual result per selected test case.

    Select the cases with one of: ids (comma separated or JSON array of tree leaf ids,
    becomes selection.leafsInclude), leafs_include (explicit JSON array) or filter_id
    (saved filter); ids and leafs_include are mutually exclusive. The API field is
    leafsInclude: there is no leafIds and no rql in the selection. assignees: comma
    separated user logins; tags_json: [{"id": 3, "name": "regress"}].
    Returns {ok, launchId, name, projectId}.
    """
    pid = _pid(project_id)
    if leafs_include and ids:
        raise TestOpsError("pass either ids or leafs_include, not both")
    selected = _ids(leafs_include, "leafs_include") if leafs_include else _ids(ids, "ids")
    if not selected and filter_id is None:
        raise TestOpsError("one of ids, leafs_include, filter_id is required")
    body = _bulk_run_body(
        launch_name=launch_name,
        project_id=pid,
        leafs_include=selected,
        filter_id=filter_id,
        assignees=[a.strip() for a in (assignees or "").split(",") if a.strip()],
        tags=_json_arg(tags_json, "tags_json"),
        release_id=release_id,
    )
    data = _api("POST", "/api/testcase/bulk/run/new", body=body)
    return _answer(data, launchId=data.get("id"), **_pick(data, ("name", "projectId")))
