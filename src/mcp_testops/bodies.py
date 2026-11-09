"""Request bodies as pure functions, so the contract tests validate exactly what is sent."""

from typing import Any

from .client import TestOpsError
from .config import TEST_STATUSES


def _drop_none(payload: dict) -> dict:
    return {k: v for k, v in payload.items() if v is not None}


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


def _patch_body(clear: bool, **fields: Any) -> dict:
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
