"""Tools: statuses and reference dictionaries."""

from ..client import TestOpsError, _api, _paged
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
    custom_field is project scoped (project_id defaults to TESTOPS_PROJECT_ID) and accepts
    query; tag is a flat list without pagination, so query is applied here.
    """
    if kind not in REFERENCE_KINDS:
        raise TestOpsError(f"kind must be one of {', '.join(REFERENCE_KINDS)}")
    if kind == "tag":
        data = _api("GET", "/api/tag")
        tags = [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []
        if query:
            tags = [item for item in tags if query.lower() in str(item.get("name", "")).lower()]
        return {"ok": True, "kind": kind, "content": [_pick(item, ("id", "name")) for item in tags]}
    if kind == "workflow":
        path, params = "/api/workflow", {}
    elif kind == "testlayer":
        path, params = "/api/testlayer", {}
    else:
        path, params = f"/api/project/{_pid(project_id)}/cf", {"query": query or None}
    res = _paged(path, params, page=page, size=size)
    res["content"] = [_pick(item, ("id", "name")) for item in res["content"]]
    return {"ok": True, "kind": kind, **res}
