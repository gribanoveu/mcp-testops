"""Tools: statuses and reference dictionaries."""

from ..client import TestOpsError, _paged
from ..config import DEFAULT_PAGE_SIZE, REFERENCE_KINDS
from ..helpers import _guard, _pick, _pid
from ..server import mcp


@mcp.tool()
@_guard
def list_statuses(
    workflow_id: int | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """List test statuses (id, name, color) - they give status_id for create_test_case.

    workflow_id narrows the answer to one workflow. The endpoint takes no project id:
    statuses are defined by workflows, not by projects.
    """
    res = _paged("/api/status", {"workflowId": workflow_id}, page=page, size=size, sort=sort)
    res["content"] = [_pick(item, ("id", "name", "color")) for item in res["content"]]
    return {"ok": True, **res}


@mcp.tool()
@_guard
def list_reference(
    kind: str,
    project_id: int | None = None,
    query: str = "",
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
) -> str:
    """List a reference dictionary by kind: workflow, testlayer, custom_field or tag.

    Returns id and name of every entry - they are what create_test_case wants in
    workflow_id, test_layer_id and custom_fields_json.
    custom_field is project scoped (project_id defaults to TESTOPS_PROJECT_ID) and takes query;
    each custom field also carries required and singleSelect, which is what decides whether a
    value must be given and whether it is one of a list.
    tag is filtered and paged on the server: the full dictionary is hundreds of thousands of
    entries, so pass query (a piece of the tag name) to get the ones you need.
    """
    if kind not in REFERENCE_KINDS:
        raise TestOpsError(f"kind must be one of {', '.join(REFERENCE_KINDS)}")
    if kind == "tag":
        # /api/tag hands back the whole dictionary - 224 333 entries, 9.5 MB on a real stand -
        # and ignores page, size and search. /api/tag/suggest filters and pages server-side.
        res = _paged("/api/tag/suggest", {"query": query or None}, page=page, size=size)
        res["content"] = [_pick(item, ("id", "name")) for item in res["content"]]
        return {"ok": True, "kind": kind, **res}
    if kind == "workflow":
        path, params = "/api/workflow", {}
    elif kind == "testlayer":
        path, params = "/api/testlayer", {}
    else:
        path, params = f"/api/project/{_pid(project_id)}/cf", {"query": query or None}
    res = _paged(path, params, page=page, size=size)
    keys = ("id", "name", "required", "singleSelect") if kind == "custom_field" else ("id", "name")
    res["content"] = [_pick(item, keys) for item in res["content"]]
    return {"ok": True, "kind": kind, **res}
