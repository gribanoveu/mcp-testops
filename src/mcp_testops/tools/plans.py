"""Tools: test plans."""

from ..bodies import _patch_body, _test_plan_body
from ..client import TestOpsError, _api, _paged
from ..config import DEFAULT_PAGE_SIZE
from ..helpers import _answer, _guard, _json_arg, _pick, _pid
from ..server import mcp, _write


@mcp.tool()
@_guard
def list_test_plans(
    project_id: int | None = None,
    search: str = "",
    tree_id: int | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
) -> str:
    """List test plans of a project: id, name, projectId, baseRql, testCasesCount.

    project_id defaults to TESTOPS_PROJECT_ID; search narrows by name.
    """
    pid = _pid(project_id)
    res = _paged(
        "/api/testplan",
        {"projectId": pid, "search": search or None, "treeId": tree_id},
        page=page,
        size=size,
    )
    res["content"] = [
        _pick(item, ("id", "name", "projectId", "baseRql", "testCasesCount"))
        for item in res["content"]
    ]
    return {"ok": True, "projectId": pid, **res}


@mcp.tool()
@_guard
def get_test_plan(test_plan_id: int) -> str:
    """Get one test plan: id, name, projectId, baseRql, testCasesCount, treeSelection."""
    data = _api("GET", f"/api/testplan/{test_plan_id}")
    keys = ("id", "name", "projectId", "baseRql", "testCasesCount", "treeSelection")
    return {"ok": True, **_pick(data, keys)}


@_write
def create_test_plan(
    name: str,
    project_id: int | None = None,
    base_rql: str = "",
    tree_id: int | None = None,
    tree_selection_json: str = "",
) -> str:
    """Create a test plan and return {ok, id, name, projectId}.

    base_rql is the AQL selection of the plan (e.g. tag.name = "smoke").
    tree_selection_json: {"leafsInclude": [1001], "inverted": false} - the plan takes
    TreeSelectionDto, which has no filterId (that one belongs to running cases).
    """
    pid = _pid(project_id)
    body = _test_plan_body(
        project_id=pid,
        name=name,
        base_rql=base_rql or None,
        tree_id=tree_id,
        tree_selection=_json_arg(tree_selection_json, "tree_selection_json"),
    )
    data = _api("POST", "/api/testplan", body=body)
    return _answer(data, **_pick(data, ("id", "name", "projectId")))


@_write
def update_test_plan(
    test_plan_id: int,
    name: str = "",
    base_rql: str = "",
    tree_id: int | None = None,
    tree_selection_json: str = "",
    clear: bool = False,
) -> str:
    """Update fields of a test plan; only the arguments you pass are sent.

    An empty string means "leave the field alone" unless clear=true, where an empty string
    clears the field. tree_selection_json: {"leafsInclude": [1001], "inverted": false}.
    """
    body = _patch_body(
        clear,
        name=name,
        baseRql=base_rql,
        treeId=tree_id,
        treeSelection=_json_arg(tree_selection_json, "tree_selection_json"),
    )
    if not body:
        raise TestOpsError("nothing to update: pass at least one field")
    data = _api("PATCH", f"/api/testplan/{test_plan_id}", body=body)
    return _answer(data, **_pick(data, ("id", "name", "projectId")))


@_write
def delete_test_plan(test_plan_id: int) -> str:
    """Delete a test plan; the API answers 204. The test cases themselves stay."""
    data = _api("DELETE", f"/api/testplan/{test_plan_id}")
    return _answer(data, testPlanId=test_plan_id)
