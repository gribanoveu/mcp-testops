---
name: testops-mcp
description: How to work with Allure TestOps through the testops MCP server - find test cases and read their steps, search with AQL, run cases in a launch, record test results, read launch statistics and the history of a test case. Use when a task mentions Allure TestOps, test cases, test plans, launches, test results, or tools such as list_test_cases, search_test_cases, run_test_cases, add_test_result.
---

# Работа с Allure TestOps через MCP

Сервер отдаёт 30 инструментов: 17 read и 13 write. Любой ответ — JSON-строка: успех
`{"ok": true, ...}`, ошибка `{"ok": false, "error": "HTTP 404 on GET /api/testcase/1: test case not found"}`.
Исключений инструменты не бросают, поэтому ошибку читай из поля `error`, а не из падения вызова.

## 1. Не угадывай идентификаторы

`project_id` приходит из `list_projects`; если задан `TESTOPS_PROJECT_ID`, его можно не передавать вовсе.
`status_id`, `workflow_id`, `test_layer_id` — только из справочников:

- `list_statuses(workflow_id=…)` → `{id, name, color}`;
- `list_reference("workflow")`, `list_reference("testlayer")`,
  `list_reference("custom_field", project_id=…)`.

Придуманный `status_id` вернёт 400 или, хуже, создаст кейс с чужим статусом.

## 2. Сначала читай, потом меняй

| Вопрос | Инструмент |
|---|---|
| какие есть проекты | `list_projects(search=…)` |
| список кейсов проекта (только строки) | `list_test_cases(project_id=…)` |
| найти кейсы по имени или AQL | `search_test_cases(name=…)` / `search_test_cases(rql=…)` |
| проверить AQL до поиска | `validate_aql(rql=…)` → `{valid, count}` |
| один кейс целиком | `get_test_case(id)` |
| шаги кейса | `get_test_case_steps(id)` |
| где гонялся кейс | `get_test_case_history(test_case_id=…)` |
| тест-планы | `list_test_plans(project_id=…)`, `get_test_plan(id)` |
| запуски проекта | `list_launches(project_id=…)` |
| результаты запуска | `list_test_results(launch_id=…)`, `get_test_result(id)`, `get_launch_statistic(launch_id)` |

`get_test_case` **не содержит шагов** — в ответе стоит `"steps_not_included": true`, шаги читает
`get_test_case_steps`. В `list_test_cases` только строки: ни описания, ни шагов.

## 3. Рецепты

### AQL: что стенд действительно принимает

Грамматика — [docs.qameta.io/reference/aql](https://docs.qameta.io/reference/aql), сверено на живом
стенде. Подстрока — только `~=`, и имена полей не совпадают с полями DTO:

- `name ~= "логин"` — подстрока; `name = "Точное имя"`, `name != "x"`;
- `tag = "smoke"`, `tag in ["smoke", "regress"]`, `not tag = "smoke"` — не `tag.name`;
- `status = "Active"`, `workflow = "Default Manual"`, `layer = "API"` — не `status.name`/`testLayer`;
- `automation = true`, `flaky = false`, `muted = true` — не `automated`;
- `cf["Severity"] = "high"`, `cfv in ["high"]`, `role["Owner"] = "user1"`;
- `id >= 100`, `createdDate > 1672531200000` — даты epoch-мс, без кавычек;
- условия — `and` / `or` (у `and` приоритет выше), группировка — скобками.

Неверный запрос — `400 invalid.aql`, `validate_aql` отвечает `{valid: false}`. Поэтому сначала
`validate_aql`, потом `search_test_cases`.

### Найти кейс и прочитать его

1. `search_test_cases(name="login")` — имя превращается в AQL `name ~= "login"` на сервере, клиентской
   фильтрации нет.
2. Для сложного условия: `validate_aql(rql='tag = "smoke"')` → `{valid, count}`; если `valid`,
   тот же `rql` в `search_test_cases`.
3. `get_test_case(id)` → тексты, статус, теги; `get_test_case_steps(id)` → дерево шагов
   (у кейса без сценария — `steps: []`).

### Узнать, в каких прогонах гонялся кейс

`get_test_case_history(test_case_id=…, project_id=…)` → строки
`{testResultId, launchId, launchName, status, start, duration}`. Подробности строки —
`get_test_result(testResultId)`. Сузить: `launch_id=…` (один запуск) или `search=…` (текст результата).

### Прогнать кейсы в новом запуске

1. Отобрать кейсы: `search_test_cases(...)` → их `id`. Для `run_test_cases` это id **листьев** дерева.
2. `run_test_cases(launch_name="Регресс 2026-11-09", ids="1001,1002")` → `launchId`.
   Вместо `ids` можно `leafs_include="[1001,1002]"` или сохранённый `filter_id=…`; `ids` и
   `leafs_include` вместе — ошибка.
3. `list_test_results(launch_id=…)` — что получилось; `get_launch_statistic(launch_id=…)` — сводка
   `{status: count}` без листания.

Прогон создаётся **с ручными результатами**: по одному на каждый кейс.

### Записать результат в существующий запуск

1. `create_launch(name="Ручной прогон", project_id=…)` → `id`.
2. `add_test_result(launch_id=…, name="Login smoke", status="failed", message="…", duration=1300,
   test_case_id=…)` — `test_case_id` обязателен (без него стенд отвечает 500), `status` только из
   `failed | broken | passed | skipped | unknown | in_progress`, иначе ошибка без запроса. `duration`,
   `start`, `stop` — миллисекунды.
3. `close_launch(launch_id=…)` — после закрытия результаты только читаются. Передумали —
   `reopen_launch(launch_id=…)`.

### Создать кейс с шагами

1. `create_test_case(name="Login smoke", project_id=…, status_id=…, tags_json='[{"id": 3, "name": "smoke"}]')`
   → `id`. Справочники — по тегам из `list_reference`.
2. `add_test_case_step(test_case_id=…, body="Открыть форму")` — ровно один из `body`, `attachment_id`,
   `shared_step_id`; `parent_step_id` делает шаг вложенным.
3. Проверить: `get_test_case_steps(id)`.

### Убрать за собой

- `delete_test_case(id, force=True)` — мягкое удаление (`202`), кейс уходит в корзину; восстановления
  инструментом нет;
- `delete_launch(launch_id)` — вместе с результатами;
- `delete_test_plan(test_plan_id)` — кейсы остаются.

### Тест-план

`create_test_plan(name="Smoke", project_id=…, base_rql='tag = "smoke"',
tree_selection_json='{"leafsInclude": [1001]}')`; правка — `update_test_plan(id, name=…)`, тело
собирается только из переданных полей, `clear=true` позволяет очистить строковое поле.

## 4. Как передавать аргументы

- **Сложные структуры — JSON-строкой**: `tags_json`, `links_json`, `members_json`,
  `custom_fields_json`, `scenario_json`, `tree_selection_json`. Точные формы — в docstring инструмента.
  `tags_json` — `[{"id": 3, "name": "smoke"}]` (id обязателен), `members_json` — роль объектом
  `{"id": 1, "name": "MEMBER"}`, `custom_fields_json` — `[{"customField": {"id": 12, "name": "Severity"},
  "name": "high"}]`.
- **Пагинация**: `page` с 0, `size` по умолчанию 50 и не больше 100; в ответе `totalElements`,
  `totalPages`, `number` — по ним видно, что выборка не вся.
- **Сортировка**: `sort="createdDate,DESC"` — одно поле, направление вторым; несколько полей стенд не
  принимает (`400 unsupported sort field`).
- **Справочники**: `list_reference("workflow")`, `"testlayer"`, `"custom_field"`; теги —
  `list_reference("tag", query="smoke")`: словарь огромный (сотни тысяч), без `query` вернётся только его
  начало.
- **Фильтры списков**: `list_projects(search=…)` сужает сервер (параметр `query` внутри); у запусков
  `list_launches(search=…)` превращается в AQL, а сложное — `list_launches(rql='tag = "smoke" and
  closed = true')`; у планов фильтра на сервере нет, `search` сужает только полученную страницу.

- **`clear`** в `update_test_case`/`update_test_plan`: без него пустая строка означает «не менять поле»,
  с ним — «очистить».

## 5. Чего инструменты не умеют

- Нет дерева кейсов, общих шагов, дефектов, вложений и импорта результатов — и обходного
  generic-вызова тоже нет: если инструмента нет, задача через MCP не решается.
- В `run_test_cases` нет `rql`: выборка только `ids` / `leafs_include` / `filter_id`.
- `get_test_case` не отдаёт шаги, вложения не отдаются содержимым (только `attachmentId`).
- HTML-дубли текстов (`*Html`) вырезаны — не ищи их в ответе.

## 6. Когда ответ не тот

- `HTTP 401/403` — авторизация: сервер шлёт `Authorization: Api-Token <token>`, стенд может ждать
  `Bearer`. Это вопрос конфигурации, а не инструмента.
- `HTTP 400` с текстом про rql — синтаксис AQL: сначала `validate_aql`, потом поиск.
- `{"ok": true, "accepted": true}` — операция принята асинхронно (`202`/`204`). Если нужен id, а его
  нет в ответе — перечитай состояние через `list_*`/`get_*`.
- Пустой `content` при поиске — проверь `project_id`, а для удалённых кейсов передай `deleted=true`.

## 7. Безопасность

- `delete_*` — только по явной просьбе пользователя.
- `force=true` — только для того, что создано в этом же сценарии.
- Если write-инструментов нет в списке, сервер поднят с `TESTOPS_READ_ONLY=true` — это норма, а не
  поломка; не ищи обходных путей, а скажи, что запись отключена.

## 8. Как проверить, что сервер жив

Самый дешёвый вызов — `list_projects(search="")`: ответ `{"ok": true, "content": [...]}` означает, что
токен и адрес стенда верны. `{"ok": false, "error": "TESTOPS_TOKEN is not set"}` — сервер вообще не
стартовал, это ошибка конфигурации клиента.
