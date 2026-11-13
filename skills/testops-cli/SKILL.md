---
name: testops-cli
description: Work with Allure TestOps from the terminal through the mcp-testops CLI - search test cases with AQL, read a case and its steps, run a selection in a launch, record results, read launch statistics - without registering an MCP server, so the tools take no room in the context. Use when a task mentions Allure TestOps, TestOps test cases, launches or test results and the shell is available, or when the user does not want the testops MCP server installed.
---

# Allure TestOps from the shell

One command per call, nothing registered in the client:

```bash
npx -y @gribanoveu/mcp-testops call <tool> '<json arguments>'
```

or, with the package installed (`pip install mcp-testops` / `uvx --from git+https://github.com/gribanoveu/mcp-testops`):

```bash
python -m mcp_testops call <tool> '<json arguments>'
```

Both start the server, make one call, print the answer and exit. **stdout carries only the answer**
(JSON of the tool), **stderr carries the log** (`GET /api/... -> 200 in 40 ms`) — pipe stdout, ignore stderr.

Three ways to look before you call:

```bash
… call --list                       # 30 tools: name and the first line of the docstring
… call --schema search_test_cases   # the argument schema of one tool
… call get_test_case '{"test_case_id": 17}'
```

Exit code `0` means the tool answered — even when the answer is `{"ok": false, "error": "HTTP 404 ..."}`:
failures are data here, so read the `error` field. Exit code `1` means the call never reached the tool:
broken JSON, a missing required argument (`1 validation error for get_projectArguments`), or no token.

## Settings

The same `TESTOPS_*` environment variables as the server, read from the shell of each command:

```bash
export TESTOPS_TOKEN=...                  # required, Api-Token
export TESTOPS_BASE_URL=https://testops.net
export TESTOPS_PROJECT_ID=65              # default project for tools that take project_id
export TESTOPS_READ_ONLY=true             # optional: the write tools then answer "read-only mode"
```

Arguments are JSON, so quote them in single quotes: `'{"search": "login"}'`. A string inside needs its
own escaping — `'{"tags_json": "[{\"id\": 3, \"name\": \"smoke\"}]"}'` — and that nested JSON-string form is
what the write tools expect for `tags_json`, `links_json`, `scenario_json`, `tree_selection_json`,
`custom_fields_json`.

## When the settings are missing

The command says what it needs instead of failing silently:

```
$ … call --list
TESTOPS_TOKEN is not set: the token goes to the stand as `Authorization: Api-Token <token>`.
  export TESTOPS_TOKEN=<api token>            # from your TestOps profile; never commit it
  …
```

What to do, in order:

1. **Ask the user — do not go looking for the token.** Say plainly what is missing: "the CLI needs
   `TESTOPS_TOKEN` — the API token from TestOps, user menu → API token — and optionally the stand
   address". Never read other applications' config files hunting for a secret, never invent a value, never
   reuse a password. If the user says a token is already configured somewhere, let them point at it.
2. **Hand over the exact commands for their platform.** The syntax differs, and `export` is meaningless on
   Windows:

   | Shell | Command |
   |---|---|
   | macOS / Linux | `export TESTOPS_TOKEN=<api token>` |
   | PowerShell | `$env:TESTOPS_TOKEN = "<api token>"` |
   | cmd.exe | `set TESTOPS_TOKEN=<api token>` |

   The optional ones are the same shape: `TESTOPS_BASE_URL` (default `https://testops.net`),
   `TESTOPS_PROJECT_ID`, `TESTOPS_VERIFY_SSL=true`.
3. **One command, one shell.** Many shell tools start a fresh shell per command, so an `export` does not
   reach the next one. On macOS/Linux prefix the call itself; PowerShell has no inline prefix, so set the
   variable and run in the same line:

   ```bash
   TESTOPS_TOKEN=… TESTOPS_BASE_URL=https://testops.net npx -y @gribanoveu/mcp-testops call list_projects '{}'
   ```

   ```powershell
   $env:TESTOPS_TOKEN="…"; npx -y @gribanoveu/mcp-testops call list_projects '{}'
   ```

4. **Keep it out of the repository.** Not in code, not in a committed `.env`, not in a note file, not in
   the chat log if you can avoid it: the user's shell profile or the client's own settings are for this.
5. **Check that it works:** `… call list_projects '{"search": ""}'` → `{"ok": true, …}`. A `401`/`403`
   now carries its own hint: `Api-Token` versus `Bearer`, or this token has no access to the project.
6. **Project id:** a tool called without `project_id` answers `project_id is required (or set
   TESTOPS_PROJECT_ID)` — either pass it or add `TESTOPS_PROJECT_ID` next to the token.

## Recipes

### Find cases and read one

```bash
… call search_test_cases '{"name": "login"}'            # the name becomes AQL name ~= "login"
… call validate_aql '{"rql": "tag = \"smoke\""}'         # {"valid": true, "count": 12} before searching
… call search_test_cases '{"rql": "tag = \"smoke\" and status = \"Active\""}'
… call get_test_case '{"test_case_id": 17}'
… call get_test_case_steps '{"test_case_id": 17}'        # steps: children, sharedStep, attachments by id
```

`list_test_cases` gives rows for a whole project; `get_test_case` gives texts and has **no steps** — the
scenario is a separate call. AQL syntax, every field and the mistakes it invites are in **aql.md** beside
this file.

### Where did a case run

```bash
… call get_test_case_history '{"test_case_id": 17}'       # rows: testResultId, launchId, status, start
… call get_test_result '{"test_result_id": 156580259}'    # the full result of one row
```

### Run a selection

```bash
… call run_test_cases '{"launch_name": "Regression 2026-11-13", "ids": "1001,1002"}'   # -> launchId
… call list_test_results '{"launch_id": 4242}'
… call get_launch_statistic '{"launch_id": 4242}'        # {"passed": 10, "failed": 2}
```

`ids` are tree leaf ids; `leafs_include='[1001,1002]'` or a saved `filter_id` work instead. There is no
`rql` in a selection.

### Record a result in an existing launch

```bash
… call create_launch '{"name": "Manual run"}'                                   # -> id
… call add_test_result '{"launch_id": 4242, "name": "Login smoke", "status": "failed",
                        "message": "element not found", "duration": 1300, "test_case_id": 17}'
… call close_launch '{"launch_id": 4242}'                                       # results become read-only
```

`test_case_id` is required (the stand answers 500 without it); `status` is one of
`failed | broken | passed | skipped | unknown | in_progress`.

### Create a case with steps

```bash
… call list_statuses '{"workflow_id": 1}'                                # ids for status_id
… call create_test_case '{"name": "Login smoke", "status_id": 3}'        # -> id
… call add_test_case_step '{"test_case_id": 17, "body": "Open the form"}'
… call add_test_case_step '{"test_case_id": 17, "body": "Fill the login", "parent_step_id": 501}'
… call get_test_case_steps '{"test_case_id": 17}'                        # verify
```

### Clean up

```bash
… call delete_test_case '{"test_case_id": 17, "force": true}'   # soft-delete -> bin, no restore tool
… call delete_launch '{"launch_id": 4242}'
… call delete_test_plan '{"test_plan_id": 8}'                    # the cases stay
```

Delete only what the user asked to delete, and `force` only for what this same run created.

## Things that bite

- **`search=` does not filter most lists.** Projects filter on `query`; launches filter with AQL on
  `/api/launch/__search` (`… call list_launches '{"rql": "tag = \"smoke\""}'`); test plans have no server
  filter, so `search` narrows only the fetched page.
- **Tags are a huge dictionary:** `list_reference '{"kind": "tag"}'` answers the whole base. Always pass
  `query`: `'{"kind": "tag", "query": "smoke"}'`.
- **Paging:** `page` starts at 0, `size` defaults to 50 and stops at 100; the answer carries
  `totalElements`/`totalPages`/`number`.
- **Sorting is one field:** `'{"sort": "createdDate,DESC"}'`; several fields answer
  `400 unsupported sort field`.
- **An empty or `403` answer** is usually a wrong `project_id` (a foreign project answers `403`, not
  `404`), and deleted cases need `'{"deleted": true}'`.
- **`--list` and `--schema` need the token too**, because the command starts the server before asking
  anything.
- The CLI has no server-side state: every command pays a process start (~0.3 s). For a long chain of
  calls, the MCP server (`testops-mcp` skill) is cheaper; for one or two lookups this is lighter.

## What it cannot do

No case tree, no shared-step editing, no defects, no attachments (only their ids), no result import, no
generic "any path under /api" call. `TESTOPS_READ_ONLY=true` makes the write tools answer
`{"ok": false, "error": "read-only mode"}`.
