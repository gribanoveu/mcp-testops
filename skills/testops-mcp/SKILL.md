---
name: testops-mcp
description: Work with Allure TestOps through the testops MCP server - find test cases and read their steps, search with AQL, run cases in a launch, record test results, read launch statistics and the history of a test case. Use when a task mentions Allure TestOps, test cases, test plans, launches, test results, or tools such as list_test_cases, search_test_cases, run_test_cases, add_test_result.
---

# Work with Allure TestOps through MCP

The server exposes 30 tools: 17 read and 13 write. Every answer is a JSON string - success
`{"ok": true, ...}`, failure `{"ok": false, "error": "HTTP 404 on GET /api/testcase/1: test case not found"}`.
The tools never raise, so read the reason out of the `error` field instead of treating the call as broken.

The full query language is in **aql.md** beside this file: every field of test cases, results and
launches, the operators, dates, subfields and the examples. Read it before writing anything more
complex than `tag = "smoke"`.

## 1. Do not guess identifiers

`project_id` comes from `list_projects`; when `TESTOPS_PROJECT_ID` is set on the server you can leave it
out entirely. `status_id`, `workflow_id` and `test_layer_id` come from the reference tools only:

- `list_statuses(workflow_id=...)` -> `{id, name, color}`;
- `list_reference("workflow")`, `list_reference("testlayer")`,
  `list_reference("custom_field", project_id=...)`.

An invented `status_id` answers 400 or, worse, creates a case in a status nobody meant.

## 2. Read before you change

| The question | The tool |
|---|---|
| which projects exist | `list_projects(search=...)` |
| the cases of a project, rows only | `list_test_cases(project_id=...)` |
| find cases by name or by AQL | `search_test_cases(name=...)` / `search_test_cases(rql=...)` |
| check an AQL query before searching | `validate_aql(rql=...)` -> `{valid, count}` |
| one case in full | `get_test_case(id)` |
| the steps of a case | `get_test_case_steps(id)` |
| where a case has run | `get_test_case_history(test_case_id=...)` |
| test plans | `list_test_plans(project_id=...)`, `get_test_plan(id)` |
| launches of a project | `list_launches(project_id=...)` |
| results of a launch | `list_test_results(launch_id=...)`, `get_test_result(id)`, `get_launch_statistic(launch_id)` |

`get_test_case` **does not carry steps** - the answer says `"steps_not_included": true`, and the steps
come from `get_test_case_steps`. `list_test_cases` returns rows: no descriptions, no steps.

## 3. The five rules of AQL that cost the most

Checked against a live stand; the rest is in aql.md.

- Substring matching is `~=` only: `name ~= "login"`. A bare `~` answers `400 invalid.aql`.
- Field names are not the DTO's: `tag = "smoke"` (not `tag.name`), `status = "Active"` (not
  `status.name`), `workflow = "Default Manual"`, `layer = "API"` (not `testLayer`), `automation = true`
  (not `automated`).
- `tag in ["smoke", "regress"]`, `not tag = "smoke"`, `!="`, `and` / `or` with parentheses.
- Dates are epoch **milliseconds**, unquoted: `createdDate > 1672531200000`.
- Validate first: `validate_aql` answers `{valid, count}`; on an invalid query the search itself answers
  `400 invalid.aql` and the turn is wasted.

## 4. Recipes

### Find a case and read it

1. `search_test_cases(name="login")` - the name becomes AQL `name ~= "login"` on the server; nothing is
   filtered client-side.
2. For a compound condition: `validate_aql(rql='tag = "smoke"')` -> `{valid, count}`, then the same
   `rql` in `search_test_cases`.
3. `get_test_case(id)` -> texts, status, tags; `get_test_case_steps(id)` -> the step tree (a case
   without a scenario answers `steps: []`; a step that points at a shared step carries
   `sharedStep: {id, name, steps}`).

### Find out where a case ran

`get_test_case_history(test_case_id=..., project_id=...)` -> rows of
`{testResultId, launchId, launchName, status, start, duration}`. Details of one row come from
`get_test_result(testResultId)`. Narrow it with `launch_id=...` (one launch) or `search=...`
(result text).

### Run cases in a new launch

1. Pick the cases: `search_test_cases(...)` -> their ids. For `run_test_cases` these are tree **leaf**
   ids.
2. `run_test_cases(launch_name="Regression 2026-11-09", ids="1001,1002")` -> `launchId`.
   `leafs_include="[1001,1002]"` or a saved `filter_id=...` work instead of `ids`; passing `ids` and
   `leafs_include` together is an error.
3. `list_test_results(launch_id=...)` for the rows, `get_launch_statistic(launch_id=...)` for the
   `{status: count}` summary without paging.

The launch is created **with manual results**, one per case.

### Record a result in an existing launch

1. `create_launch(name="Manual run", project_id=...)` -> `id`.
2. `add_test_result(launch_id=..., name="Login smoke", status="failed", message="...", duration=1300,
   test_case_id=...)` - `test_case_id` is required (the stand answers 500 without it), `status` is one
   of `failed | broken | passed | skipped | unknown | in_progress`, anything else is refused before the
   request. `duration`, `start` and `stop` are milliseconds.
3. `close_launch(launch_id=...)` makes the results read-only; `reopen_launch(launch_id=...)` undoes that.

### Create a case with steps

1. `create_test_case(name="Login smoke", project_id=..., status_id=..., tags_json='[{"id": 3, "name": "smoke"}]')`
   -> `id`. Tag ids come from `list_reference("tag", query=...)`.
2. `add_test_case_step(test_case_id=..., body="Open the form")` - exactly one of `body`,
   `attachment_id`, `shared_step_id`; `parent_step_id` nests the step.
3. Verify with `get_test_case_steps(id)`.

### Clean up after yourself

- `delete_test_case(id, force=True)` soft-deletes (`202`) and puts the case in the bin; there is no
  restore tool;
- `delete_launch(launch_id)` removes the launch with its results;
- `delete_test_plan(test_plan_id)` leaves the cases alone.

### A test plan

`create_test_plan(name="Smoke", project_id=..., base_rql='tag = "smoke"',
tree_selection_json='{"leafsInclude": [1001]}')`; change it with `update_test_plan(id, name=...)` - the
body is built from the fields you pass only, and `clear=true` empties a string field.

## 5. How to pass arguments

- **Structured values go in as JSON strings**: `tags_json`, `links_json`, `members_json`,
  `custom_fields_json`, `scenario_json`, `tree_selection_json`. The exact shape is in the tool's
  docstring. `tags_json` -> `[{"id": 3, "name": "smoke"}]` (the id is required), `members_json` -> the
  role as an object `{"id": 1, "name": "MEMBER"}`, `custom_fields_json` ->
  `[{"customField": {"id": 12, "name": "Severity"}, "name": "high"}]`.
- **Paging**: `page` starts at 0, `size` defaults to 50 and stops at 100; the answer carries
  `totalElements`, `totalPages` and `number`, so a partial selection is visible.
- **Sorting**: `sort="createdDate,DESC"` - one field, direction second; the stand refuses several
  fields (`400 unsupported sort field`).
- **References**: `list_reference("workflow")`, `"testlayer"`, `"custom_field"`; tags are
  `list_reference("tag", query="smoke")` - the dictionary holds hundreds of thousands of entries, and
  without `query` you get only its beginning.
- **List filters**: `list_projects(search=...)` narrows on the server (the API parameter is `query`);
  `list_launches(search=...)` becomes AQL, and anything complex goes through
  `list_launches(rql='tag = "smoke" and closed = true')`; test plans have no server-side filter, so
  `search` narrows the page that was already fetched.
- **`clear`** in `update_test_case` / `update_test_plan`: without it an empty string means "leave the
  field alone", with it "empty the field".

## 6. What the tools cannot do

- There is no case tree, no shared-step editor, no defects, no attachments and no result import - and no
  generic "any path under /api" tool to work around it: if the tool is missing, the task does not go
  through this MCP.
- `run_test_cases` takes no `rql`: a selection is `ids` / `leafs_include` / `filter_id`.
- `get_test_case` has no steps, and attachments come back as `attachmentId`, never as content.
- The HTML duplicates of text fields (`*Html`) are stripped - do not look for them.

## 7. When the answer is not what you expected

- `HTTP 401` or `403` - authentication: the server sends `Authorization: Api-Token <token>` and the
  stand may want `Bearer`. That is a configuration question, not a tool problem. The error text now
  carries that hint, along with the second cause: `403` also means this token has no access to that
  project.
- `HTTP 400` mentioning rql - the AQL syntax: `validate_aql` first, search second.
- `{"ok": true, "accepted": true}` - the operation was accepted asynchronously (`202`/`204`). If an id
  you need is missing from the answer, read the state back with `list_*` / `get_*`.
- An empty `content` on a search - check `project_id`, and for deleted cases pass `deleted=true`.

## 8. Safety

- Call `delete_*` only when the user asked for a deletion.
- `force=true` only for what this same run created.
- When the write tools are missing from the list, the server runs with `TESTOPS_READ_ONLY=true` - that is
  deliberate, not a breakage: say that writing is off instead of looking for a way around it.

## 9. Is the server alive, and are the settings right

The cheapest call is `list_projects(search="")`: `{"ok": true, "content": [...]}` means the token and the
stand address are right. Then read the failure, because each one has a different fix:

- `{"ok": false, "error": "TESTOPS_TOKEN is not set: ... export TESTOPS_TOKEN=<api token> ..."}` — the
  server reads its own environment only, never your shell or a `.env` in the project. The token belongs in
  the client's `env` block (or its config dialog); where the client supports it, write
  `"TESTOPS_TOKEN": "${env:TESTOPS_TOKEN}"` and keep the value outside the repository. If the user has a
  token somewhere already — `~/.kibo/mcp.json`, `~/.cursor/mcp.json`, `~/.claude.json`, a project
  `.mcp.json`, `mcpServers.*.env` — it can be reused; do not print it and do not commit it.
- `401`/`403` — the token scheme or the access: the server sends `Api-Token`, the stand may want `Bearer`,
  and a project the token cannot see answers `403` too.
- `{"ok": false, "error": "project_id is required (or set TESTOPS_PROJECT_ID)"}` — pass `project_id`, or add
  `TESTOPS_PROJECT_ID` to the same `env` block.
- No tools at all in the client's list, or an error about the command — the client cannot start the
  process: check the `command`/`args` (an absolute path for a binary or a virtualenv python), then the
  client's log.
