# 03. Спецификация инструментов

29 инструментов: 16 read, 13 write. Generic `api_request` сознательно не выводим — почему, в §7.
Ниже — сигнатура, эндпоинт, тело, что возвращаем и на что наступить нельзя. Схемы — в
`../openapi/key-schemas.json`, эндпоинты — в `../openapi/api-inventory.md`.

Все инструменты объявляются штатным декоратором официального SDK — `@mcp.tool()` (`MCPServer` в v2,
`FastMCP` в v1) и возвращают `str` с JSON. Собственный слой над протоколом, реестр инструментов или
свой JSON-RPC не пишем.

## 0. Общие правила

1. **`project_id` везде опционален**, если задан `TESTOPS_PROJECT_ID`; если не задан и не передан — ошибка
   `{"ok": false, "error": "project_id is required (or set TESTOPS_PROJECT_ID)"}`. В каждом ответе листинга
   возвращаем использованный `projectId`, чтобы модель не путала проекты.
2. **Пагинация:** `page` (с 0), `size` (по умолчанию 50, максимум 100), `sort` (строка `"property,ASC"`,
   можно `"a,ASC,b,DESC"`). Возвращаем `{content, totalElements, totalPages, number, size}` — не голый массив.
3. **Ответ — компактный JSON.** HTML-дубли (`descriptionHtml`, `preconditionHtml`, `postconditionHtml`,
   `expectedResultHtml`) вырезаются. Для полного кейса возвращаем: `id`, `name`, `fullName`, `projectId`,
   `status`, `workflow`, `testLayer`, `tags`, `links`, `automated`, `flaky`, `deleted`, `duration`,
   `precondition`, `description`, `expectedResult`, `postcondition`, `createdDate`, `lastModifiedDate`.
4. **Ошибки:** любой инструмент возвращает `{"ok": false, "error": "<HTTP 4xx on GET /path: message>"}`.
   Не бросать исключения, не возвращать HTML.
5. **Сложные поля — JSON-строки** (`*_json`): разбираются `json.loads`, при ошибке — `{"ok": false, "error": "invalid JSON in tags_json: ..."}`.
6. **Write-инструменты** при `TESTOPS_READ_ONLY=true` не регистрируются.

## 1. Сводная таблица

| # | Инструмент | Тип | Эндпоинт |
|---|---|---|---|
| 1 | `list_projects` | read | `GET /api/project` |
| 2 | `get_project` | read | `GET /api/project/{id}` |
| 3 | `list_test_cases` | read | `GET /api/testcase` |
| 4 | `get_test_case` | read | `GET /api/testcase/{id}` |
| 5 | `get_test_case_steps` | read | `GET /api/testcase/{id}/step` |
| 6 | `search_test_cases` | read | `GET /api/testcase/__search` |
| 7 | `validate_aql` | read | `GET /api/testcase/query/validate` |
| 8 | `list_test_plans` | read | `GET /api/testplan` |
| 9 | `get_test_plan` | read | `GET /api/testplan/{id}` |
| 10 | `list_launches` | read | `GET /api/launch` |
| 11 | `get_launch` | read | `GET /api/launch/{id}` |
| 12 | `get_launch_statistic` | read | `GET /api/launch/{id}/statistic` |
| 13 | `list_test_results` | read | `GET /api/testresult` |
| 14 | `get_test_result` | read | `GET /api/testresult/{id}` |
| 15 | `list_statuses` | read | `GET /api/status` |
| 16 | `list_reference` | read | `/api/workflow`, `/api/testlayer`, `/api/project/{projectId}/cf`, `/api/tag` |
| 17 | `create_test_case` | write | `POST /api/testcase` |
| 18 | `update_test_case` | write | `PATCH /api/testcase/{id}` |
| 19 | `delete_test_case` | write | `DELETE /api/testcase/{id}` |
| 20 | `add_test_case_step` | write | `POST /api/testcase/step` |
| 21 | `create_test_plan` | write | `POST /api/testplan` |
| 22 | `update_test_plan` | write | `PATCH /api/testplan/{id}` |
| 23 | `delete_test_plan` | write | `DELETE /api/testplan/{id}` |
| 24 | `create_launch` | write | `POST /api/launch` |
| 25 | `close_launch` / `reopen_launch` | write | `POST /api/launch/{id}/close`, `/reopen` |
| 26 | `delete_launch` | write | `DELETE /api/launch/{id}` |
| 27 | `add_test_result` | write | `POST /api/testresult` |
| 28 | `run_test_cases` | write | `POST /api/testcase/bulk/run/new` |

---

## 2. Проекты

### `list_projects(search: str = None, favorite: bool = None, page: int = 0, size: int = 50) -> str`

`GET /api/project` с `params={search?, favorite?, page, size, sort="name,ASC"}`.
Возвращает `{content:[{id, name, abbr, isPublic, isVersioned, launchCount, automationPercent}], totalElements, totalPages, number}`.
Не отдавать `descriptionHtml`.

### `get_project(project_id: int) -> str`

`GET /api/project/{project_id}` → `ProjectDto` (белый список из п. 0.3).

---

## 3. Кейсы

### `list_test_cases(project_id=None, page=0, size=50, sort=None) -> str`

`GET /api/testcase` с `projectId`, `page`, `size`, `sort?`.
Возвращает строки `TestCaseRowDto`: у кейса здесь **нет описания и шагов** — только `id`, `name`,
`status`, `automated`, `flaky`, `testLayer`. Docstring обязан это сказать, иначе модель решит, что
получила кейс целиком.

### `get_test_case(test_case_id: int) -> str`

`GET /api/testcase/{test_case_id}` → `TestCaseDto` (белый список). В ответе явно
`"steps_not_included": true`, чтобы агент пошёл за `get_test_case_steps`.

### `get_test_case_steps(test_case_id: int, as_tree: bool = True) -> str`

`GET /api/testcase/{test_case_id}/step` → `NormalizedScenarioDto`.

- `as_tree=True` (по умолчанию): собираем дерево из `root` + `scenarioSteps` по `children`, каждый узел —
  `{id, body, expectedResult, attachmentId, sharedStepId, children:[...]}`.
- `as_tree=False`: отдаём `scenarioSteps` как есть (словарь по id).
- Вложение `attachments` (толстые DTO) не отдаём — только `attachmentId`; за содержимым — отдельно.

### `search_test_cases(project_id=None, rql: str = "", name: str = "", deleted: bool = False, page=0, size=50, sort="") -> str`

`GET /api/testcase/__search` с `projectId`, `rql`, `deleted`, `page`, `size`, `sort?` → `PageTestCaseDto`.
Нужен один из `rql` или `name`: **`name` превращается в AQL `name ~ "…"` на сервере**, клиентской
выгрузки проекта нет (Д2), без обоих — ошибка `rql or name is required`. Docstring — с примерами:
`name ~ "логин"`, `status.name = "Черновик"`, `tag.name = "smoke"`. Примеры пометить как проверяемые
на стенде (`06-open-questions.md`, вопрос 2), потому что синтаксис AQL спецификацией не описан.

### `validate_aql(project_id=None, rql: str, deleted: bool = False) -> str`

`GET /api/testcase/query/validate` → `AqlValidateResponseDto` `{valid, count}`. Дешёвая проверка перед
`search_test_cases`; `count` — сколько кейсов попадёт в выборку.

### `create_test_case(name: str, project_id=None, description=None, precondition=None, postcondition=None,
expected_result=None, status_id=None, workflow_id=None, test_layer_id=None, tags_json=None, links_json=None,
members_json=None, custom_fields_json=None, scenario_json=None, automated=None) -> str`

`POST /api/testcase`, тело `TestCaseCreateV2Dto`. Собираем только не-`None` поля (`projectId` обязателен,
`name` обязателен). Возвращаем `{ok: true, id, name, projectId, url?}` — `id` обязателен, без него агент
не сможет добавить шаги.

Примеры для docstring:

```json
tags_json     = [{"id": 3, "name": "smoke"}]
links_json    = [{"name": "JIRA", "type": "issue", "url": "https://jira/browse/ABC-1"}]
scenario_json = {"steps": [{"type": "body", "body": "Открыть форму"}]}
```

Важно: у `TestTagDto` в схеме обязателен `id`, поэтому тег по имени сначала ищем в `GET /api/tag`
(плоский массив, без пагинации).

### `update_test_case(test_case_id: int, ...те же поля, что у create..., clear: bool = False) -> str`

`PATCH /api/testcase/{test_case_id}`, тело `TestCasePatchV2Dto` — только переданные поля (у patch все
необязательны). `clear=True` означает «пустая строка = очистить поле», иначе пустые строки отбрасываем
(сейчас `_compact` их пропускает в тело — источник неожиданных затираний).

### `delete_test_case(test_case_id: int, force: bool = False) -> str`

`DELETE /api/testcase/{test_case_id}?force=<bool>` → `202`. Возвращаем `{ok: true, accepted: true}`.
Docstring: без `force` кейс, у которого есть результаты прогонов, может не удалиться.

### `add_test_case_step(test_case_id: int, body: str = None, parent_step_id: int = None,
attachment_id: int = None, shared_step_id: int = None) -> str`

`POST /api/testcase/step`, тело `ScenarioStepCreateDto` (`testCaseId`, `parentId`, `body`,
`attachmentId`, `sharedStepId`) → `{createdStepId, scenario}`. Возвращаем `createdStepId` и
`{"steps_count": n}` (полный `scenario` не нужен, его можно прочитать отдельно).
Нужен ровно один из `body`/`attachment_id`/`shared_step_id` — иначе ошибка аргументов.

---

## 4. Тест-планы

### `list_test_plans(project_id=None, search=None, tree_id=None, page=0, size=50) -> str`

`GET /api/testplan` → `{content:[{id, name, projectId, baseRql, testCasesCount}], ...}`.

### `get_test_plan(test_plan_id: int) -> str`

`GET /api/testplan/{test_plan_id}` → `{id, name, projectId, baseRql, testCasesCount, treeSelection}`.

### `create_test_plan(name: str, project_id=None, base_rql=None, tree_id=None, tree_selection_json=None) -> str`

`POST /api/testplan`, тело `TestPlanCreateDto` (`name`, `projectId`, `baseRql`, `treeId`, `treeSelection`).

### `update_test_plan(test_plan_id: int, name=None, base_rql=None, tree_id=None, tree_selection_json=None) -> str`

`PATCH /api/testplan/{test_plan_id}`, тело `TestPlanPatchDto`.

### `delete_test_plan(test_plan_id: int) -> str`

`DELETE /api/testplan/{test_plan_id}`.

---

## 5. Запуски и результаты

### `list_launches(project_id=None, search=None, filter_id=None, page=0, size=50, sort=None) -> str`

`GET /api/launch` → `oneOf(PageLaunchPreviewDto, PageLaunchDto)`. Разбираем терпимо: общие поля
(`id`, `name`, `projectId`, `closed`, `createdDate`) + `statistic` при наличии. Возвращаем компактно:
`{id, name, closed, createdDate, statistic:{passed, failed, broken, skipped, unknown}}`.

### `get_launch(launch_id: int) -> str`

`GET /api/launch/{launch_id}` → `LaunchDto` (белый список + `tags`, `releaseId`).

### `get_launch_statistic(launch_id: int) -> str`

`GET /api/launch/{launch_id}/statistic` — сводка по статусам. Дешевле, чем листать результаты.

### `list_test_results(launch_id: int, page=0, size=50, sort=None) -> str`

`GET /api/testresult?launchId` → `PageTestResultDto`. Компактно: `{id, name, testCaseId, status, duration,
message, trace, start, stop}`.

### `get_test_result(test_result_id: int) -> str`

`GET /api/testresult/{test_result_id}` → `TestResultDto` (белый список, без `*Html`).

### `create_launch(name: str, project_id=None, autoclose=None, release_id=None, tags_json=None, links_json=None) -> str`

`POST /api/launch`, тело `LaunchCreateDto` (`name`, `projectId` обязательны). Возвращаем `{ok, id, name}`.

### `close_launch(launch_id: int) -> str` / `reopen_launch(launch_id: int) -> str`

`POST /api/launch/{launch_id}/close` и `/reopen` — тела нет. Ответ может быть пустым (успех) — возвращаем
`{ok: true, launch_id, action: "closed"}`.

### `delete_launch(launch_id: int) -> str`

`DELETE /api/launch/{launch_id}` → `204`. Docstring: удаляются и все результаты прогона.

### `add_test_result(launch_id: int, name: str, status: str, test_case_id: int = None, duration: int = None,
message: str = None, trace: str = None, start: int = None, stop: int = None, description=None,
precondition=None, postcondition=None, expected_result=None, tags_json=None, links_json=None,
custom_fields_json=None) -> str`

`POST /api/testresult`, тело `TestResultCreateV2Dto`, required `launchId`, `name`, `status`.
`status` — `TestStatus` (`failed|broken|passed|skipped|unknown|in_progress`); валидируем **до** запроса и
возвращаем понятную ошибку со списком допустимых значений. `duration`, `start`, `stop` — миллисекунды
(int64).

### `run_test_cases(launch_name: str, project_id=None, leafs_include: str = "", ids: str = "",
filter_id: int = None, assignees: str = "", tags_json=None, release_id: int = None) -> str`

`POST /api/testcase/bulk/run/new`, тело `TestCaseBulkRunNewLaunchDto`.

```json
{
  "launchName": "Регресс 2026-11-09",
  "selection": {"projectId": 65, "leafsInclude": [1001, 1002]},
  "assignees": ["ivanov"],
  "tags": [{"id": 3, "name": "regress"}]
}
```

- `ids` — строка `"1001,1002"` (или список через запятую) → превращается в `leafsInclude`;
- `leafs_include` — JSON-массив, если нужен явный контроль;
- **поле называется `leafsInclude`**; `leafIds` в `TestCaseTreeSelectionDto` не существует — на этом
  сломан текущий код (см. `04-current-implementation.md`, дефект 1);
- вместо `ids` можно задать `filter_id` (тогда `selection` берёт выборку с сервера);
- **поля `rql` в `TestCaseTreeSelectionDto` нет** — есть `search` (строка), семантика не подтверждена
  (`06-open-questions.md`, вопрос 12), поэтому аргумента `rql` у инструмента нет;
- `tags` здесь — `LaunchTagDto` (а не `TestTagDto`), форма та же `{id, name}`;
- ответ — `LaunchDto`: возвращаем `{ok, launchId, name, url?}`; docstring предупреждает, что прогон
  создаётся **с ручными результатами** (по одному на кейс).

---

## 6. Справочники

### `list_statuses(workflow_id: int = None, page=0, size=50, sort="") -> str`

`GET /api/status` с `workflowId?` → `{content:[{id, name, color}], ...}`. Нужен, чтобы получить `statusId`
для `create_test_case`. Параметра `projectId` у эндпоинта в спеке нет: статусы задаются workflow.

### `list_reference(kind: str, project_id=None, query="", page=0, size=50) -> str`

Один инструмент вместо четырёх — `kind` из `workflow | testlayer | custom_field | tag`:

| `kind` | Эндпоинт |
|---|---|
| `workflow` | `GET /api/workflow` |
| `testlayer` | `GET /api/testlayer` |
| `custom_field` | `GET /api/project/{projectId}/cf` (**не** deprecated `/api/cf`) |
| `tag` | `GET /api/tag` (плоский массив `TestTagDto`, без пагинации — `query` фильтрует на клиенте) |

Неизвестный `kind` → `{"ok": false, "error": "kind must be one of workflow, testlayer, custom_field, tag"}`.
`custom_field` требует `project_id` (или `TESTOPS_PROJECT_ID`), остальные — нет.

---

## 7. Generic `api_request` — сознательно нет

В первом варианте спеки здесь был escape hatch «любой `/api/...` под денилистом». От него отказались:

- денилист по принципу «разрешено всё, что не перечислено» провалился на практике: в нём стоял
  `/api/registration`, которого в снимке нет, а регистрация — `POST /api/register`, то есть создание
  учётной записи проходило мимо правил;
- обход через `%61ccount` и `..` пришлось закрывать нормализацией пути — и каждый следующий обход
  пришлось бы закрывать так же;
- generic-инструмент обнуляет смысл остальных: `POST /api/testcase/bulk/remove` или
  `DELETE /api/testcase/{id}` проходят через него без валидации тела и без предупреждений;
- цена — пересматривать денилист на каждом этапе, пока не найдётся очередная дыра.

Что вместо него:

- всё, что реально нужно агенту, закрыто 29 именованными инструментами с проверенными телами;
- справочники (`list_statuses`, `list_reference`) закрывают Д6 — без них нечем заполнить `statusId`,
  `workflowId`, `testLayerId`;
- чего нет среди инструментов (дерево, общие шаги, дефекты, вложения), через MCP недоступно вообще:
  если это понадобится, добавляется именованный инструмент с телом из схемы, а не generic-вызов.

Правило для следующих этапов: **не вводить generic-инструмент обратно**, ни за флагом, ни «только для
GET». Если агенту не хватает охвата, расширять список именованных инструментов по `api-inventory.md`.
