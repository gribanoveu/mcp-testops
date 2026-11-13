"""Tools: test cases, their steps, search and history."""

from ..bodies import _patch_body, _step_body, _test_case_body
from ..client import TestOpsError, _api, _paged
from ..config import DEFAULT_PAGE_SIZE
from ..helpers import _aql_text, _answer, _guard, _json_arg, _pick, _pid
from ..server import mcp, _write


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


@mcp.tool()
@_guard
def list_test_cases(
    project_id: int | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """List test cases of a project as rows: id, name, status, automated.

    A row carries only what the stand puts there - on a 2026 stand that is id, name, status,
    automated; testLayer and flaky appear when the row has them. Rows carry no description
    and no steps: read one case with get_test_case and its steps with get_test_case_steps.
    Deleted cases are not listed; search_test_cases(deleted=true) shows the bin.
    project_id defaults to TESTOPS_PROJECT_ID. sort: "property,ASC|DESC", e.g.
    "createdDate,DESC"; the stand takes one field only.
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
    """Get one test case by id: texts, status, workflow, testLayer, tags, links, flags.

    Flags are automated, flaky, deleted and duration. The answer does NOT contain the
    scenario/steps (TestCaseDto has none) and says so with "steps_not_included": true -
    read them with get_test_case_steps.
    """
    data = _api("GET", f"/api/testcase/{test_case_id}")
    return {"ok": True, **_pick(data, TEST_CASE_KEYS), "steps_not_included": True}


def _scenario_roots(by_id: dict) -> list[dict]:
    """Roots of a scenario the API did not name: steps no other step lists as a child."""
    child_ids = {str(child) for step in by_id.values() for child in step.get("children") or []}
    return [step for key, step in by_id.items() if key not in child_ids]


def _step_node(step: dict, by_id: dict, seen: frozenset = frozenset(), shared=None) -> dict:
    node = _pick(step, ("id", "body", "expectedResult", "attachmentId", "sharedStepId"))
    children = []
    for child_id in step.get("children") or []:
        child = by_id.get(str(child_id))
        if child and child_id not in seen:
            children.append(_step_node(child, by_id, seen | {child_id}, shared))
    node["children"] = children
    if node.get("sharedStepId") and shared:
        # Without this the step is an id with no content: the stand keeps the shared step
        # and its own steps in two maps beside the scenario.
        node["sharedStep"] = _shared_node(node["sharedStepId"], shared)
    return node


def _shared_node(shared_id, shared, seen: frozenset = frozenset()) -> dict:
    """A shared step with its own steps resolved, so the tree reads without a second call."""
    by_id, steps_by_id = shared
    key = str(shared_id)
    shared_step = by_id.get(key) or {}
    node = {"id": shared_step.get("id", shared_id), "name": shared_step.get("body") or shared_step.get("name")}
    steps = []
    for child_id in shared_step.get("children") or []:
        child = steps_by_id.get(str(child_id))
        if child and str(child_id) not in seen:
            steps.append(_step_node(child, steps_by_id, seen | {str(child_id)}, shared))
    if steps:
        node["steps"] = steps
    return node


@mcp.tool()
@_guard
def get_test_case_steps(test_case_id: int, as_tree: bool = True) -> str:
    """Read the scenario (steps) of a test case.

    as_tree=true (default) returns nested steps: {id, body, expectedResult, attachmentId,
    sharedStepId, children}. as_tree=false returns the raw scenarioSteps map by id.
    A case without a scenario answers "steps": [].
    A shared step appears as a node with sharedStepId plus a "sharedStep" object: {id, name,
    steps} with its own steps resolved. Attachment contents are not inlined either - only
    attachmentId.
    """
    data = _api("GET", f"/api/testcase/{test_case_id}/step")
    shared_by_id = data.get("sharedSteps") or {}
    shared = (shared_by_id, data.get("sharedStepScenarioSteps") or {}) if shared_by_id else None
    if not as_tree:
        answer = {"ok": True, "testCaseId": test_case_id, "scenarioSteps": data.get("scenarioSteps") or {}}
        if shared:
            answer["sharedSteps"] = shared_by_id
            answer["sharedStepScenarioSteps"] = shared[1]
        return answer
    by_id = data.get("scenarioSteps") or {}
    root = data.get("root") or {}
    if isinstance(root, int):
        root = by_id.get(str(root)) or {}
    # The stand wraps the first-level steps in a container root: {"children": [...]} and nothing
    # of its own. Returning it as one more step only adds a level to unwrap, so an id alone does
    # not make the root a step - only content of its own does.
    root_is_step = bool(root) and any(
        root.get(key) for key in ("body", "expectedResult", "attachmentId", "sharedStepId")
    )
    if not by_id:
        # A case without a scenario answers an empty map and a bare {"children": []} root;
        # walking that would invent one step with every field null.
        steps = []
    elif root_is_step:
        steps = [_step_node(root, by_id, shared=shared)]
    elif root.get("children"):
        steps = [
            _step_node(by_id[str(child)], by_id, frozenset({str(child)}), shared)
            for child in root["children"]
            if str(child) in by_id
        ]
    else:
        steps = [_step_node(step, by_id, frozenset({str(step.get("id"))}), shared) for step in _scenario_roots(by_id)]
    return {"ok": True, "testCaseId": test_case_id, "steps": steps}


@mcp.tool()
@_guard
def get_test_case_history(
    test_case_id: int,
    project_id: int | None = None,
    launch_id: int | None = None,
    search: str = "",
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> str:
    """Which launches ran a test case, and with what result.

    Answers "where was this case run": each row is {testResultId, launchId, launchName, status,
    start, stop, duration}. launch_id narrows to one launch, search narrows by result text.
    project_id defaults to TESTOPS_PROJECT_ID. The row of this endpoint carries no message and
    no testedBy - for those and the rest of the result, call get_test_result(testResultId).
    """
    pid = _pid(project_id)
    res = _paged(
        "/api/testcase/history",
        {
            "projectId": pid,
            "testCaseId": test_case_id,
            "launchId": launch_id,
            "search": search or None,
        },
        page=page,
        size=size,
        sort=sort,
    )
    rows = []
    for item in res["content"]:
        launch = item.get("launch") or {}
        row = {"testResultId": item.get("id"), "launchId": launch.get("id"), "launchName": launch.get("name")}
        row.update(_pick(item, ("status", "start", "stop", "duration", "message", "testedBy")))
        rows.append(row)
    res["content"] = rows
    return {"ok": True, "projectId": pid, "testCaseId": test_case_id, **res}


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

    Give either rql or name. name becomes the AQL query name ~= "<name>" on the server
    (substring match), nothing is filtered client-side.

    Test-case AQL, as the stand accepts it (docs.qameta.io/reference/aql):
      name ~= "login" (substring), name = "Login smoke" (exact), name != "x"
      tag = "smoke", tag in ["smoke", "regress"], not tag = "smoke"
      status = "Active", workflow = "Default Manual", layer = "API"
      automation = true, flaky = false, muted = true
      cf["Severity"] = "high", cfv in ["high"], role["Owner"] = "user1"
      id >= 100, createdDate > 1672531200000 (dates are epoch milliseconds, unquoted)
      conditions join with and / or, group with parentheses, negate with not

    Field names are not the DTO's: automation (not automated), layer (not testLayer),
    tag = "smoke" (not tag.name = "smoke"). Run validate_aql first when unsure.
    Returns {content: [case fields], rql, totalElements, totalPages, number}.
    """
    pid = _pid(project_id)
    query = (rql or "").strip()
    if not query:
        if not (name or "").strip():
            raise TestOpsError("rql or name is required")
        query = f'name ~= "{_aql_text(name.strip())}"'
    res = _paged(
        "/api/testcase/__search",
        {"projectId": pid, "rql": query, "deleted": True if deleted else None},
        page=page,
        size=size,
        sort=sort,
    )
    res["content"] = [_pick(item, TEST_CASE_KEYS) for item in res["content"]]
    return {"ok": True, "projectId": pid, "rql": query, **res}


@mcp.tool()
@_guard
def validate_aql(project_id: int | None = None, rql: str = "", deleted: bool = False) -> str:
    """Check an AQL query (the API calls it rql) before running search_test_cases.

    Returns {ok, valid, count}: count is how many test cases the query selects, so a typo
    is caught before a real search. project_id defaults to TESTOPS_PROJECT_ID;
    deleted=true counts removed cases too. rql is required.
    """
    pid = _pid(project_id)
    if not (rql or "").strip():
        raise TestOpsError("rql is required")
    data = _api(
        "GET",
        "/api/testcase/query/validate",
        params={"projectId": pid, "rql": rql, "deleted": True if deleted else None},
    )
    return {"ok": True, "projectId": pid, **_pick(data, ("valid", "count"))}


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
      members_json       [{"id": 7, "name": "ivanov", "role": {"id": 1, "name": "MEMBER"}}]
                         (role is an object RoleDto, not a plain string)
      custom_fields_json [{"customField": {"id": 12, "name": "Severity"}, "name": "high"}]
                         (the API requires both id and name of the custom field)
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
    return _answer(data, **_pick(data, ("id", "name", "projectId")))


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
    members_json: str = "",
    custom_fields_json: str = "",
    scenario_json: str = "",
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
        "members": _json_arg(members_json, "members_json"),
        "customFields": _json_arg(custom_fields_json, "custom_fields_json"),
        "scenario": _json_arg(scenario_json, "scenario_json"),
        "automated": automated,
        "duration": duration,
    }
    body = _patch_body(clear, **fields)
    if not body:
        raise TestOpsError("nothing to update: pass at least one field")
    data = _api("PATCH", f"/api/testcase/{test_case_id}", body=body)
    return _answer(data, **_pick(data, ("id", "name", "projectId")))


@_write
def delete_test_case(test_case_id: int, force: bool = False) -> str:
    """Delete a test case; the API answers 202 and moves it to the trash.

    Without force a case that has run results may stay; force=true deletes it anyway,
    together with its scenario. Restoring a case is not exposed as a tool.
    """
    data = _api("DELETE", f"/api/testcase/{test_case_id}", params={"force": True if force else None})
    return _answer(data, testCaseId=test_case_id, forced=force)


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
    return _answer(
        data,
        createdStepId=data.get("createdStepId"),
        steps_count=len(scenario.get("scenarioSteps") or {}),
    )
