"""Every request body a tool builds is validated against the OpenAPI snapshot.

A body that does not match the schema is the defect class this file exists for:
`run_test_cases` shipped `leafIds` instead of `leafsInclude` and created empty launches.
"""

import json
import pathlib

import pytest
from jsonschema import Draft202012Validator

import mcp_testops as testops

ROOT = pathlib.Path(__file__).resolve().parent.parent
with open(ROOT / "openapi" / "api-docs.json", encoding="utf-8") as fh:
    SPEC = json.load(fh)


def validator(schema_name: str) -> Draft202012Validator:
    schema = {"components": SPEC["components"], "$ref": f"#/components/schemas/{schema_name}"}
    return Draft202012Validator(schema)


def assert_valid(schema_name: str, body: dict) -> None:
    errors = sorted(validator(schema_name).iter_errors(body), key=lambda e: list(e.path))
    assert not errors, f"{schema_name} rejects {body}: " + "; ".join(
        f"{list(e.path)}: {e.message}" for e in errors
    )


STEP_SCHEMAS = ("AttachmentStepDto", "BodyStepDto", "ExpectedBodyStepDto", "SharedStepStepDto")


def test_create_test_case_body():
    body = testops._test_case_body(
        project_id=65,
        name="Login smoke",
        description="check the login form",
        precondition="user exists",
        expected_result="dashboard",
        status_id=5,
        workflow_id=2,
        test_layer_id=1,
        tags=[{"id": 3, "name": "smoke"}],
        links=[{"name": "JIRA", "type": "issue", "url": "https://jira/browse/ABC-1"}],
        scenario={"steps": [{"type": "body", "body": "Open the form"}]},
        members=[{"id": 7, "name": "ivanov", "role": {"id": 1, "name": "MEMBER"}}],
        custom_fields=[{"customField": {"id": 12, "name": "Severity"}, "name": "high"}],
        automated=True,
    )
    # TestCaseScenarioV2Dto.steps is oneOf over four DTOs that differ only by optional
    # fields, so every step matches all four and oneOf rejects any step at all. The step
    # is validated against each DTO separately; see docs/06-open-questions.md, question 5.
    without_scenario = {key: value for key, value in body.items() if key != "scenario"}
    assert_valid("TestCaseCreateV2Dto", without_scenario)
    for step_schema in STEP_SCHEMAS:
        assert_valid(step_schema, body["scenario"]["steps"][0])
    assert body["projectId"] == 65 and body["name"] == "Login smoke"


def test_update_test_case_body_drops_empty_strings():
    body = testops._test_case_patch_body(False, name="Renamed", description="", precondition="")
    assert_valid("TestCasePatchV2Dto", body)
    assert body == {"name": "Renamed"}


def test_update_test_case_body_clears_with_flag():
    body = testops._test_case_patch_body(True, description="")
    assert_valid("TestCasePatchV2Dto", body)
    assert body == {"description": ""}


def test_add_step_body():
    assert_valid("ScenarioStepCreateDto", testops._step_body(42, body="Open the form"))
    assert_valid("ScenarioStepCreateDto", testops._step_body(42, attachment_id=7))
    assert_valid("ScenarioStepCreateDto", testops._step_body(42, body="child", parent_id=1))
    # No request DTO in the snapshot sets additionalProperties: false, so a schema check
    # alone lets a renamed field through; the body itself is pinned down here.
    assert testops._step_body(42, body="Open", parent_id=1) == {
        "testCaseId": 42,
        "parentId": 1,
        "body": "Open",
    }


def test_add_step_body_requires_exactly_one_source():
    with pytest.raises(testops.TestOpsError, match="exactly one of"):
        testops._step_body(42)
    with pytest.raises(testops.TestOpsError, match="exactly one of"):
        testops._step_body(42, body="x", shared_step_id=9)


def test_create_test_plan_body():
    body = testops._test_plan_body(
        project_id=65,
        name="Smoke plan",
        base_rql='tag.name = "smoke"',
        tree_selection={"leafsInclude": [1001, 1002], "inverted": False},
    )
    assert_valid("TestPlanCreateDto", body)
    assert body == {
        "projectId": 65,
        "name": "Smoke plan",
        "baseRql": 'tag.name = "smoke"',
        "treeSelection": {"leafsInclude": [1001, 1002], "inverted": False},
    }


def test_create_launch_body():
    body = testops._launch_body(
        project_id=65,
        name="Regress 2026-11-09",
        autoclose=True,
        release_id=4,
        tags=[{"id": 3, "name": "regress"}],
    )
    assert_valid("LaunchCreateDto", body)
    assert body == {
        "projectId": 65,
        "name": "Regress 2026-11-09",
        "autoclose": True,
        "releaseId": 4,
        "tags": [{"id": 3, "name": "regress"}],
    }


def test_add_test_result_body():
    body = testops._test_result_body(
        launch_id=10,
        name="Login smoke",
        status="failed",
        test_case_id=42,
        duration=1300,
        message="expected dashboard, got error",
        trace="stack",
        start=1,
        stop=2,
    )
    assert_valid("TestResultCreateV2Dto", body)
    assert body == {
        "launchId": 10,
        "name": "Login smoke",
        "status": "failed",
        "testCaseId": 42,
        "duration": 1300,
        "message": "expected dashboard, got error",
        "trace": "stack",
        "start": 1,
        "stop": 2,
    }


def test_add_test_result_rejects_unknown_status():
    with pytest.raises(testops.TestOpsError, match="status must be one of"):
        testops._test_result_body(launch_id=10, name="x", status="ok")


def test_run_test_cases_body_uses_leafs_include():
    body = testops._bulk_run_body(
        launch_name="Regress",
        project_id=65,
        leafs_include=[1001, 1002],
        assignees=["ivanov"],
        tags=[{"id": 3, "name": "regress"}],
    )
    assert_valid("TestCaseBulkRunNewLaunchDto", body)
    assert body["selection"] == {"projectId": 65, "leafsInclude": [1001, 1002]}
    assert "leafIds" not in body["selection"]


def test_run_test_cases_body_from_filter():
    body = testops._bulk_run_body(launch_name="Regress", project_id=65, filter_id=7)
    assert_valid("TestCaseBulkRunNewLaunchDto", body)
    assert body["selection"] == {"projectId": 65, "filterId": 7}
