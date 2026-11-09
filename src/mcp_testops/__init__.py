"""MCP server for Allure TestOps.

Transport is stdio; everything that depends on the stand and the project comes
from ``TESTOPS_*`` environment variables (see README).
"""

import functools
import json
import os
import time
from typing import Any

import httpx
from mcp.server import MCPServer

SERVER_NAME = os.getenv("MCP_SERVER_NAME", "testops")
BASE_URL = os.getenv("TESTOPS_BASE_URL", "https://testops.moscow.alfaintra.net").rstrip("/")
TOKEN = os.getenv("TESTOPS_TOKEN")
DEFAULT_PROJECT_ID = os.getenv("TESTOPS_PROJECT_ID")
TIMEOUT = float(os.getenv("TESTOPS_TIMEOUT", "60"))


def _flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


VERIFY_SSL = _flag("TESTOPS_VERIFY_SSL")
READ_ONLY = _flag("TESTOPS_READ_ONLY")

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
RETRY_STATUSES = {429, 500, 502, 503, 504}
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 0.5

TEST_STATUSES = ("failed", "broken", "passed", "skipped", "unknown", "in_progress")
ALLOWED_METHODS = ("DELETE", "GET", "PATCH", "POST", "PUT")
FORBIDDEN_PREFIXES = (
    "/api/account",
    "/api/mfa",
    "/api/admin",
    "/api/registration",
    "/api/invite",
    "/api/integration",
    "/api/token",
)

mcp = MCPServer(SERVER_NAME)


class TestOpsError(Exception):
    """Returned to the model as {"ok": false, "error": ...}, never raised past a tool."""


# --- plumbing ---------------------------------------------------------------


def _dump(payload: Any) -> str:
    """Compact JSON: a listing of 50 items must not eat the model's context."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _guard(fn):
    """Turn exceptions into data: a raise inside a tool costs the agent a turn."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return _dump(fn(*args, **kwargs))
        except TestOpsError as exc:
            return _dump({"ok": False, "error": str(exc)})
        except httpx.HTTPError as exc:
            return _dump({"ok": False, "error": f"{type(exc).__name__}: {exc}"})

    return wrapper


def _write(fn):
    """Register a mutating tool only when TESTOPS_READ_ONLY is off."""
    return _guard(fn) if READ_ONLY else mcp.tool()(_guard(fn))


_client: httpx.Client | None = None


def _http() -> httpx.Client:
    """One client per process: connection pool and TLS handshake are not free."""
    global _client
    if _client is None:
        _client = httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
            verify=VERIFY_SSL,
            headers={"Authorization": f"Api-Token {TOKEN or ''}"},
        )
    return _client


def _error_text(resp: httpx.Response) -> str:
    message = ""
    try:
        data = resp.json()
    except ValueError:
        data = None
    if isinstance(data, dict):
        message = str(data.get("message") or data.get("error") or "")
    where = f"{resp.request.method} {resp.request.url.path}"
    return f"HTTP {resp.status_code} on {where}: {message or resp.reason_phrase}"


def _send(method: str, path: str, params: dict | None = None, body: Any = None) -> httpx.Response:
    """Retry only idempotent calls: a replayed POST creates a second entity."""
    attempts = RETRY_ATTEMPTS if method in ("GET", "HEAD") else 1
    for attempt in range(attempts):
        try:
            resp = _http().request(method, path, params=params, json=body)
        except httpx.TransportError:
            if attempt + 1 == attempts:
                raise
        else:
            if resp.status_code not in RETRY_STATUSES or attempt + 1 == attempts:
                return resp
        time.sleep(RETRY_BACKOFF * 2**attempt)
    raise TestOpsError(f"{method} {path}: no response")


def _api(method: str, path: str, params: dict | None = None, body: Any = None) -> Any:
    query = {k: v for k, v in (params or {}).items() if v is not None}
    resp = _send(method, path, query, body)
    if resp.status_code in (202, 204):
        return {"ok": True, "accepted": True}
    if not resp.is_success:
        raise TestOpsError(_error_text(resp))
    if not resp.content.strip():
        return {"ok": True}
    try:
        return resp.json()
    except ValueError:
        raise TestOpsError(f"non-JSON response from {method} {path} (HTTP {resp.status_code})")


def _paged(
    path: str,
    params: dict | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> dict:
    """One place that knows the Page*Dto envelope, so no tool re-implements it."""
    query = {**(params or {}), "page": max(0, page), "size": max(1, min(size, MAX_PAGE_SIZE))}
    if sort:
        query["sort"] = sort
    data = _api("GET", path, params=query)
    if not isinstance(data, dict) or "content" not in data:
        raise TestOpsError(f"unexpected paged response from GET {path}")
    return {
        "content": data.get("content") or [],
        "totalElements": data.get("totalElements"),
        "totalPages": data.get("totalPages"),
        "number": data.get("number"),
        "size": data.get("size"),
    }


def _pid(project_id: int | None) -> int:
    raw = project_id if project_id is not None else DEFAULT_PROJECT_ID
    if raw is None or raw == "":
        raise TestOpsError("project_id is required (or set TESTOPS_PROJECT_ID)")
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise TestOpsError(f"project_id must be an integer, got {raw!r}")


def _json_arg(value: str | None, name: str) -> Any:
    if value is None or value == "":
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise TestOpsError(f"invalid JSON in {name}: {exc}")


def _ids(value: str | None, name: str) -> list[int]:
    text = (value or "").strip()
    if not text:
        return []
    items = _json_arg(text, name) if text.startswith("[") else text.split(",")
    if not isinstance(items, list):
        raise TestOpsError(f"{name} must be a comma separated list or a JSON array")
    try:
        return [int(str(item).strip()) for item in items if str(item).strip()]
    except ValueError:
        raise TestOpsError(f"invalid id list in {name}: {value!r}")


def _drop_none(payload: dict) -> dict:
    return {k: v for k, v in payload.items() if v is not None}


def _pick(data: dict, keys: tuple[str, ...]) -> dict:
    """Whitelist of fields: keeps *Html duplicates and server noise out of the answer."""
    return {k: data[k] for k in keys if data.get(k) is not None}


STATUS_KEYS = ("passed", "failed", "broken", "skipped", "unknown", "in_progress")


def _statistic(raw: Any) -> dict:
    if isinstance(raw, list):
        return {
            item.get("status"): item.get("count")
            for item in raw
            if isinstance(item, dict) and item.get("status")
        }
    if isinstance(raw, dict):
        return {k: v for k, v in raw.items() if k in STATUS_KEYS}
    return {}


# --- request bodies (pure, so the contract tests can validate them) ----------

TEST_CASE_KEYS = (
    "id",
    "name",
    "fullName",
    "projectId",
    "status",
    "workflow",
    "testLayer",
    "tags",
    "links",
    "automated",
    "flaky",
    "deleted",
    "duration",
    "precondition",
    "description",
    "expectedResult",
    "postcondition",
    "createdDate",
    "lastModifiedDate",
)


def _test_case_body(
    project_id: int,
    name: str,
    description: str | None = None,
    precondition: str | None = None,
    postcondition: str | None = None,
    expected_result: str | None = None,
    status_id: int | None = None,
    workflow_id: int | None = None,
    test_layer_id: int | None = None,
    tags: Any = None,
    links: Any = None,
    members: Any = None,
    custom_fields: Any = None,
    scenario: Any = None,
    automated: bool | None = None,
) -> dict:
    return _drop_none(
        {
            "projectId": project_id,
            "name": name,
            "description": description,
            "precondition": precondition,
            "postcondition": postcondition,
            "expectedResult": expected_result,
            "statusId": status_id,
            "workflowId": workflow_id,
            "testLayerId": test_layer_id,
            "tags": tags,
            "links": links,
            "members": members,
            "customFields": custom_fields,
            "scenario": scenario,
            "automated": automated,
        }
    )


def _test_case_patch_body(clear: bool, **fields: Any) -> dict:
    """PATCH omits what was not passed; "" clears a field only with clear=True."""
    body = {}
    for key, value in fields.items():
        if value is None:
            continue
        if value == "" and not clear:
            continue
        body[key] = value
    return body


def _step_body(
    test_case_id: int,
    body: str | None = None,
    parent_id: int | None = None,
    attachment_id: int | None = None,
    shared_step_id: int | None = None,
) -> dict:
    if sum(value is not None for value in (body, attachment_id, shared_step_id)) != 1:
        raise TestOpsError("exactly one of body, attachment_id, shared_step_id is required")
    return _drop_none(
        {
            "testCaseId": test_case_id,
            "parentId": parent_id,
            "body": body,
            "attachmentId": attachment_id,
            "sharedStepId": shared_step_id,
        }
    )


def _test_plan_body(
    project_id: int,
    name: str,
    base_rql: str | None = None,
    tree_id: int | None = None,
    tree_selection: Any = None,
) -> dict:
    return _drop_none(
        {
            "projectId": project_id,
            "name": name,
            "baseRql": base_rql,
            "treeId": tree_id,
            "treeSelection": tree_selection,
        }
    )


def _launch_body(
    project_id: int,
    name: str,
    autoclose: bool | None = None,
    release_id: int | None = None,
    tags: Any = None,
    links: Any = None,
) -> dict:
    return _drop_none(
        {
            "projectId": project_id,
            "name": name,
            "autoclose": autoclose,
            "releaseId": release_id,
            "tags": tags,
            "links": links,
        }
    )


def _test_result_body(
    launch_id: int,
    name: str,
    status: str,
    test_case_id: int | None = None,
    duration: int | None = None,
    message: str | None = None,
    trace: str | None = None,
    start: int | None = None,
    stop: int | None = None,
    description: str | None = None,
    precondition: str | None = None,
    postcondition: str | None = None,
    expected_result: str | None = None,
    tags: Any = None,
    links: Any = None,
    custom_fields: Any = None,
) -> dict:
    if status not in TEST_STATUSES:
        raise TestOpsError(f"status must be one of {', '.join(TEST_STATUSES)}")
    return _drop_none(
        {
            "launchId": launch_id,
            "name": name,
            "status": status,
            "testCaseId": test_case_id,
            "duration": duration,
            "message": message,
            "trace": trace,
            "start": start,
            "stop": stop,
            "description": description,
            "precondition": precondition,
            "postcondition": postcondition,
            "expectedResult": expected_result,
            "tags": tags,
            "links": links,
            "customFields": custom_fields,
        }
    )


def _bulk_run_body(
    launch_name: str,
    project_id: int,
    leafs_include: list[int] | None = None,
    filter_id: int | None = None,
    assignees: list[str] | None = None,
    tags: Any = None,
    release_id: int | None = None,
) -> dict:
    selection = _drop_none(
        {"projectId": project_id, "leafsInclude": leafs_include or None, "filterId": filter_id}
    )
    return _drop_none(
        {
            "launchName": launch_name,
            "selection": selection,
            "assignees": assignees or None,
            "tags": tags,
            "releaseId": release_id,
        }
    )


# --- tools: projects --------------------------------------------------------


@mcp.tool()
@_guard
def list_projects(
    search: str = "",
    favorite: bool = False,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
) -> str:
    """List TestOps projects, ordered by name.

    search: optional substring of the project name; favorite: only starred projects.
    page starts at 0, size is capped at 100. Returns {content, totalElements, totalPages, number}
    with id, name, abbr, isPublic, isVersioned, launchCount, automationPercent per project.
    """
    res = _paged(
        "/api/project",
        {"search": search or None, "favorite": True if favorite else None},
        page=page,
        size=size,
        sort="name,ASC",
    )
    res["content"] = [
        _pick(item, ("id", "name", "abbr", "isPublic", "isVersioned", "launchCount", "automationPercent"))
        for item in res["content"]
    ]
    return {"ok": True, **res}


@mcp.tool()
@_guard
def get_project(project_id: int) -> str:
    """Get one project by id: id, name, abbr, isPublic, isVersioned, launchCount, automationPercent."""
    data = _api("GET", f"/api/project/{project_id}")
    keys = ("id", "name", "abbr", "isPublic", "isVersioned", "launchCount", "automationPercent",
            "createdDate", "lastModifiedDate")
    return {"ok": True, **_pick(data, keys)}


# --- tools: test cases ------------------------------------------------------


@mcp.tool()
@_guard
def list_test_cases(
    project_id: int | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """List test cases of a project as rows: id, name, status, automated, flaky, testLayer.

    Rows carry no description and no steps - read one case with get_test_case and its
    steps with get_test_case_steps. project_id defaults to TESTOPS_PROJECT_ID.
    sort: "property,ASC|DESC", e.g. "createdDate,DESC".
    """
    pid = _pid(project_id)
    res = _paged("/api/testcase", {"projectId": pid}, page=page, size=size, sort=sort)
    res["content"] = [
        _pick(item, ("id", "name", "status", "automated", "flaky", "testLayer"))
        for item in res["content"]
    ]
    return {"ok": True, "projectId": pid, **res}


@mcp.tool()
@_guard
def get_test_case(test_case_id: int) -> str:
    """Get one test case by id: texts, status, workflow, testLayer, tags, links.

    The answer does NOT contain the scenario/steps (TestCaseDto has none) and says so
    with "steps_not_included": true - read them with get_test_case_steps.
    """
    data = _api("GET", f"/api/testcase/{test_case_id}")
    return {"ok": True, **_pick(data, TEST_CASE_KEYS), "steps_not_included": True}


def _step_node(step: dict, by_id: dict, seen: frozenset = frozenset()) -> dict:
    node = _pick(step, ("id", "body", "expectedResult", "attachmentId", "sharedStepId"))
    children = []
    for child_id in step.get("children") or []:
        child = by_id.get(str(child_id))
        if child and child_id not in seen:
            children.append(_step_node(child, by_id, seen | {child_id}))
    node["children"] = children
    return node


@mcp.tool()
@_guard
def get_test_case_steps(test_case_id: int, as_tree: bool = True) -> str:
    """Read the scenario (steps) of a test case.

    as_tree=true (default) returns nested steps: {id, body, expectedResult, attachmentId,
    sharedStepId, children}. as_tree=false returns the raw scenarioSteps map by id.
    Attachment contents are not inlined - only attachmentId.
    """
    data = _api("GET", f"/api/testcase/{test_case_id}/step")
    if not as_tree:
        return {"ok": True, "testCaseId": test_case_id, "scenarioSteps": data.get("scenarioSteps") or {}}
    by_id = data.get("scenarioSteps") or {}
    root = data.get("root") or {}
    if isinstance(root, int):
        root = by_id.get(str(root)) or {}
    steps = [_step_node(root, by_id)] if root else []
    return {"ok": True, "testCaseId": test_case_id, "steps": steps}


@mcp.tool()
@_guard
def search_test_cases(
    project_id: int | None = None,
    rql: str = "",
    name: str = "",
    deleted: bool = False,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """Search test cases with AQL (the API calls it rql) and return full cases.

    Give either rql or name. name becomes the AQL query name ~ "<name>" on the server,
    nothing is filtered client-side. Examples (syntax to be verified on the stand):
    name ~ "login", status.name = "Draft", tag.name = "smoke".
    Returns {content: [case fields], rql, totalElements, totalPages, number}.
    """
    pid = _pid(project_id)
    query = (rql or "").strip()
    if not query:
        if not (name or "").strip():
            raise TestOpsError("rql or name is required")
        query = f'name ~ "{name.strip()}"'
    res = _paged(
        "/api/testcase/__search",
        {"projectId": pid, "rql": query, "deleted": True if deleted else None},
        page=page,
        size=size,
        sort=sort,
    )
    res["content"] = [_pick(item, TEST_CASE_KEYS) for item in res["content"]]
    return {"ok": True, "projectId": pid, "rql": query, **res}


@_write
def create_test_case(
    name: str,
    project_id: int | None = None,
    description: str = "",
    precondition: str = "",
    postcondition: str = "",
    expected_result: str = "",
    status_id: int | None = None,
    workflow_id: int | None = None,
    test_layer_id: int | None = None,
    tags_json: str = "",
    links_json: str = "",
    members_json: str = "",
    custom_fields_json: str = "",
    scenario_json: str = "",
    automated: bool | None = None,
) -> str:
    """Create a test case and return {ok, id, name, projectId}.

    name is required, project_id defaults to TESTOPS_PROJECT_ID.
    JSON-string arguments:
      tags_json          [{"id": 3, "name": "smoke"}]  (the API requires the tag id)
      links_json         [{"name": "JIRA", "type": "issue", "url": "https://jira/browse/ABC-1"}]
      members_json       [{"id": 7, "name": "ivanov", "role": "MEMBER"}]
      custom_fields_json [{"customField": {"id": 12}, "name": "value"}]
      scenario_json      {"steps": [{"type": "body", "body": "Open the form"}]}
    Ids for status_id, workflow_id and test_layer_id come from list_statuses and
    list_reference. More steps are added with add_test_case_step.
    """
    pid = _pid(project_id)
    body = _test_case_body(
        project_id=pid,
        name=name,
        description=description or None,
        precondition=precondition or None,
        postcondition=postcondition or None,
        expected_result=expected_result or None,
        status_id=status_id,
        workflow_id=workflow_id,
        test_layer_id=test_layer_id,
        tags=_json_arg(tags_json, "tags_json"),
        links=_json_arg(links_json, "links_json"),
        members=_json_arg(members_json, "members_json"),
        custom_fields=_json_arg(custom_fields_json, "custom_fields_json"),
        scenario=_json_arg(scenario_json, "scenario_json"),
        automated=automated,
    )
    data = _api("POST", "/api/testcase", body=body)
    return {"ok": True, **_pick(data, ("id", "name", "projectId"))}


@_write
def update_test_case(
    test_case_id: int,
    name: str = "",
    description: str = "",
    precondition: str = "",
    postcondition: str = "",
    expected_result: str = "",
    status_id: int | None = None,
    workflow_id: int | None = None,
    test_layer_id: int | None = None,
    tags_json: str = "",
    links_json: str = "",
    custom_fields_json: str = "",
    automated: bool | None = None,
    duration: int | None = None,
    clear: bool = False,
) -> str:
    """Update fields of a test case; only the arguments you pass are sent.

    An empty string means "leave the field alone" unless clear=true, where an empty
    string clears the field. JSON-string arguments are the same as in create_test_case.
    """
    fields = {
        "name": name,
        "description": description,
        "precondition": precondition,
        "postcondition": postcondition,
        "expectedResult": expected_result,
        "statusId": status_id,
        "workflowId": workflow_id,
        "testLayerId": test_layer_id,
        "tags": _json_arg(tags_json, "tags_json"),
        "links": _json_arg(links_json, "links_json"),
        "customFields": _json_arg(custom_fields_json, "custom_fields_json"),
        "automated": automated,
        "duration": duration,
    }
    body = _test_case_patch_body(clear, **fields)
    if not body:
        raise TestOpsError("nothing to update: pass at least one field")
    data = _api("PATCH", f"/api/testcase/{test_case_id}", body=body)
    return {"ok": True, **_pick(data, ("id", "name", "projectId"))}


@_write
def add_test_case_step(
    test_case_id: int,
    body: str = "",
    parent_step_id: int | None = None,
    attachment_id: int | None = None,
    shared_step_id: int | None = None,
) -> str:
    """Add a step to a test case scenario and return {createdStepId, steps_count}.

    Exactly one of body (step text), attachment_id, shared_step_id is required.
    parent_step_id makes the new step a child of an existing step.
    """
    step = _step_body(
        test_case_id,
        body=body or None,
        parent_id=parent_step_id,
        attachment_id=attachment_id,
        shared_step_id=shared_step_id,
    )
    data = _api("POST", "/api/testcase/step", body=step)
    scenario = data.get("scenario") or {}
    return {
        "ok": True,
        "createdStepId": data.get("createdStepId"),
        "steps_count": len(scenario.get("scenarioSteps") or {}),
    }


# --- tools: test plans ------------------------------------------------------


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
    tree_selection_json: {"leafsInclude": [1001], "filterId": 3, "inverted": false}.
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
    return {"ok": True, **_pick(data, ("id", "name", "projectId"))}


# --- tools: launches and results --------------------------------------------

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

    statistic is {passed, failed, broken, skipped, unknown} as counts. The API answers
    with two different launch shapes; both are read into this summary.
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
        summary["statistic"] = _statistic(item.get("statistic"))
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
    return {"ok": True, **_pick(data, ("id", "name", "projectId"))}


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
    return {"ok": True, **_pick(data, ("id", "name", "launchId"))}


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
    (saved filter). The API field is leafsInclude: there is no leafIds and no rql in
    the selection. assignees: comma separated user logins;
    tags_json: [{"id": 3, "name": "regress"}]. Returns {ok, launchId, name, projectId}.
    """
    pid = _pid(project_id)
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
    return {"ok": True, "launchId": data.get("id"), **_pick(data, ("name", "projectId"))}


# --- tools: escape hatch ----------------------------------------------------


@mcp.tool()
@_guard
def api_request(method: str, path: str, params_json: str = "", body_json: str = "") -> str:
    """Call any /api/... endpoint the named tools do not cover.

    method: GET, POST, PUT, PATCH or DELETE. path must start with /api - it is not
    prefixed for you, so a typo stays visible. params_json and body_json are JSON
    objects (not arrays).
    Refused: /api/account*, /api/mfa*, /api/admin*, /api/registration, /api/invite,
    /api/integration* (secrets live there), /api/token*, DELETE /api/project*, and any
    method but GET when TESTOPS_READ_ONLY=true.
    Returns {ok, data} with the response body as is, {ok, accepted} for 202/204.
    """
    verb = (method or "").strip().upper()
    if verb not in ALLOWED_METHODS:
        raise TestOpsError(f"method must be one of {', '.join(ALLOWED_METHODS)}")
    if not path.startswith("/api"):
        raise TestOpsError("path must start with /api")
    for prefix in FORBIDDEN_PREFIXES:
        if path.startswith(prefix):
            raise TestOpsError(f"{prefix}* endpoints are not available through api_request")
    if verb == "DELETE" and path.startswith("/api/project"):
        raise TestOpsError("DELETE /api/project* is not allowed")
    if READ_ONLY and verb != "GET":
        raise TestOpsError("read-only mode: only GET is allowed")
    params = _json_arg(params_json, "params_json")
    body = _json_arg(body_json, "body_json")
    for name, value in (("params_json", params), ("body_json", body)):
        if value is not None and not isinstance(value, dict):
            raise TestOpsError(f"{name} must be a JSON object")
    return {"ok": True, "data": _api(verb, path, params=params, body=body)}


def main() -> None:
    """Run the stdio server; refuses to start without a token."""
    if not TOKEN:
        raise SystemExit("TESTOPS_TOKEN is not set")
    mcp.run()
