# AQL - Allure Query Language

AQL is what Allure TestOps uses to select test cases, test results and launches in dashboards, widgets,
test plans and the API. A query is a field name and the value it must have, joined into conditions.

```sql
name = "My test"                                  exact name
name ~= "test"                                    substring - the only substring operator
name ~= "test" and createdBy = "john"             both conditions
name ~= "test" or createdBy = "john"              either one
id >= 100                                         numbers take comparison operators, unquoted
muted = true                                      booleans are the keywords true and false
not name ~= "test" and not createdBy = "john"     negation
name != "My test" and createdBy != "john"         != is the same as not =
```

Sources: <https://docs.qameta.io/reference/aql> and <https://docs.qatools.ru/aql>. Everything marked
*checked* was verified against a live stand on 2026-11-13 - that stand accepted the whole grammar below.

## Where a query goes in the API

| Purpose | Endpoint | Parameter |
|---|---|---|
| search test cases | `GET /api/testcase/__search` | `rql`, plus `projectId` |
| check a test-case query | `GET /api/testcase/query/validate` | `rql`, plus `projectId`; answers `{valid, count}` |
| search launches | `GET /api/launch/__search` | `rql`, plus `projectId` |
| a test plan's own selection | `POST /api/testplan` | `baseRql` |

In the MCP these are `search_test_cases(rql=...)`, `validate_aql(rql=...)`, `list_launches(rql=...)`
and `create_test_plan(base_rql=...)`.

## Operators

| Form | Meaning |
|---|---|
| `field = value` | equals |
| `field ~= "text"` | contains the substring; strings only, and a bare `~` is invalid |
| `field != value` | not equals |
| `not field = value` | the same negation |
| `field > value`, `>=`, `<`, `<=` | numbers and dates |
| `field in [a, b, c]` | any of the values, same as `a or b or c` |
| `field["name"] = value` | a subfield of an object, e.g. `cf["Epic"] = "Auth"` |
| `field = null`, `field is null` | the field has no value |
| `cond and cond` | both; binds tighter than `or` |
| `cond or cond` | either |
| `(cond or cond) and cond` | parentheses decide the order |

Strings are double-quoted; a value inside them needs its quote escaped as `\"`. Field values can be a
name or a numeric id for most reference-like fields (`tag = "smoke"` or `tag = 369`).

## Dates

Dates are Unix time in **milliseconds** (13 digits), unquoted, compared as numbers:

```sql
createdDate > 1672531200000 and createdDate < 1704067200000    everything created in 2023
```

`createdDate < 1569430502` is wrong - append three zeros.

## Functions (Allure TestOps 26.3.1.0 and newer)

Available in launch AQL, mostly for widgets:

| Function | Meaning |
|---|---|
| `dayStartUtc()` | today's start in UTC |
| `now()` | the current epoch, in UTC |
| `weekAgo()`, `twoWeeksAgo()` | one or two weeks back |
| `threeMonthsAgo()`, `sixMonthsAgo()` | three or six months back |
| `currentUser()` | the logged-in user |

```sql
createdDate > weekAgo()
createdBy = currentUser()
```

## Test case fields

| Field | What it matches | Example |
|---|---|---|
| `id` | case id | `id = 17` |
| `name` | case name: exact, substring, not equal | `name ~= "login"`, `name != "smoke"` |
| `tag` | case tags; true if at least one matches; name or id | `tag = "smoke"`, `tag in ["smoke", "web"]`, `tag = 369` |
| `issue` | linked tracker issues; key or id | `issue in ["AS-1", "AS-3"]`, `issue = 123` |
| `requirement` | linked requirements; name or id | `requirement = "Auth flow"`, `requirement in [72, 84]` |
| `role` | users in a test role; the role goes in brackets | `role["Owner"] = "john"`, `role[123] = "john"` |
| `member` | all users assigned to the case | `member in ["john", "jane"]` |
| `cf` | one custom field; the field goes in brackets | `cf["Epic"] = "Auth"`, `cf[123] = "Auth"` |
| `cfv` | all custom field values | `cfv in ["Auth", "Story 2"]` |
| `layer` | test layer; name or id | `layer = "API"`, `layer = 123` |
| `status` | workflow status; name or id; system statuses answer to Russian and English names | `status = "Active"`, `status = "Активный"`, `status = -3` |
| `workflow` | workflow of the case; name or id | `workflow = "Default Manual"` |
| `testPlan` | test plan the case belongs to; name or id | `testPlan = "smoke tests"` |
| `automation` | the case is automated | `automation = true` |
| `muted` | the case is in quarantine | `muted = true` |
| `flaky` | the automated case is unstable (26.3.1.0+) | `flaky = false` |
| `mutedDate` | when it went to quarantine | `mutedDate < 1569430502709` |
| `createdDate`, `createdBy` | creation | `createdBy = "john"` |
| `lastModifiedDate`, `lastModifiedBy` | last change | `lastModifiedBy = "jane"` |

## Test result fields

| Field | What it matches | Example |
|---|---|---|
| `id` | result id | `id = 17` |
| `name`, `fullName` | result name, exact or substring for `name` | `name = "Login"`, `fullName = "..."` |
| `testCase` | name of the case behind the result | `testCase = "Login smoke"` |
| `status` | execution status | `status = "failed"` |
| `category` | result category | `category = "IO Exception"` |
| `tag`, `issue`, `role`, `member`, `cf`, `cfv` | as on a test case | `tag = "smoke"` |
| `testedBy` | the engineer who ran it | `testedBy = "John Wazowsky"` |
| `ev`, `evv` | one or all environment variables | `ev["OS"] = "Linux"`, `evv in ["Linux"]` |
| `layer`, `muted` | as on a test case | `layer = "API"` |
| `hidden` | a retry or a result hidden by a user | `hidden = false` |
| `launch` | launch name or id | `launch = "release-1.0"`, `launch ~= "release"` |
| `createdDate`, `createdBy`, `lastModifiedDate`, `lastModifiedBy` | as on a test case | `createdDate > weekAgo()` |

## Launch fields

| Field | What it matches | Example |
|---|---|---|
| `id` | launch id | `id = 17` |
| `name` | launch name, exact or substring | `name = "release-1.0"`, `name ~= "release"` |
| `tag` | launch tags | `tag = "regular"`, `tag in ["release", "pre-release"]` |
| `issue` | linked issues | `issue in ["AS-1"]` |
| `job` | build job name or id | `job = "jenkins_master"` |
| `ev`, `evv` | environment variables | `ev["OS"] = "Linux"` |
| `closed` | the launch is closed | `closed = false` |
| `project` | project of the launch, id or name | `project = 657`, `project = "Shop"` |
| `createdDate`, `createdBy`, `lastModifiedDate`, `lastModifiedBy` | as on a test case | `createdDate > twoWeeksAgo()` |

## Checked against a live stand

These are the mistakes the grammar invites; each one was tried on the stand.

| Query | Result |
|---|---|
| `name ~ "login"` | `400 invalid.aql` - the substring operator is `~=` |
| `tag.name = "smoke"` | `400 invalid.aql` - it is `tag = "smoke"` |
| `status.name = "Active"` | `400 invalid.aql` - it is `status = "Active"` |
| `automated = true` | `400 invalid.aql` - it is `automation = true` |
| `testLayer = "API"` | `400 invalid.aql` - it is `layer = "API"` |
| `createdDate >= "2026-01-01"` | `400 invalid.aql` - dates are epoch milliseconds, unquoted |
| `name ~= "Сверка"` | works; Cyrillic is fine |
| `status = "Active"`, `status = -3` | both work |
| `tag in ["smoke", "regress"]` | works, 46 cases |
| `(tag = "smoke" or tag = "regressUI") and status = "Active"` | works |
| `cf["Suite"] = "x"` | works |
| `flaky = false` | works (the stand is newer than 26.3.1.0) |

A wrong query answers `400 invalid.aql` from `__search` and `{valid: false}` from `validate`. A right one
answers `{valid: true, count: N}` - `count` is how many entities it selects, which is worth checking
before a search that pages through them.

## Ready-made queries

```sql
tag = "smoke"
tag = "smoke" and status = "Active"
name ~= "login" and automation = false
createdDate > 1672531200000 and createdDate < 1704067200000
cf["Story"] = "Authentication"
role["Owner"] = null
not tag in ["nightly", "devbuild"]
id >= 1521300 and id <= 1521400
```
