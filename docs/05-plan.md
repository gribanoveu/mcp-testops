# 05. План работ

Пять этапов: M0 — подготовка папки, M1–M4 — реализация. Каждый заканчивается проверяемым
результатом и коммитом в репозиторий, в котором лежит эта папка. Этапы идут по порядку: без M1
исправления M2–M3 нечем ловить.

Источник правды — `../openapi/api-docs.json` (спека 527u04). Если спека обновилась, сначала переснимаем
снимок и смотрим дифф схем, потом трогаем код.

## M0. Подготовить папку (15–30 минут)

Внешнего репозитория нет: работа идёт в `testops-mcp/`, рядом с аналитикой. Первым делом:

- убедись, что в папке нет чужого кода (`ls`): изначально здесь только `docs/`, `openapi/` и `reference/`;
- подними каркас по `../AGENTS.md` §«Каркас проекта (в этой папке)» — `pyproject.toml`, `src/mcp_testops/`,
  `tests/` — не удаляя и не переименовывая документы;
- `../reference/` не трогай: это снимок примера, он не участвует в сборке и не должен попасть в пакет
  (добавь его в исключения `hatchling`, если он вдруг попадает в wheel).

Выход этапа: в папке есть проект, в котором `python -m mcp_testops` падает с понятным сообщением
«TESTOPS_TOKEN is not set» (значит, пакет собирается и стартует), а `04` прочитан как список
антипаттернов.

## M1. Клиент, контрактные тесты и критические исправления

**Цель:** перестать терять данные из-за неверных тел и получить сеть безопасности.

Задачи:

1. **Зафиксировать линию официального SDK MCP** и убрать из зависимостей всё лишнее:
   - v2 (рекомендована для нового кода): `mcp>=2,<3`, `from mcp.server import MCPServer`;
   - v1 (если продолжаешь готовую заготовку): `mcp>=1.0,<2`, `from mcp.server.fastmcp import FastMCP`.

   Выбор — один, записан в `pyproject.toml` и в README. Сторонние фреймворки (`fastmcp` от Prefect,
   `mcp-agent` и т.п.) не добавлять: задача — официальный SDK. Для разработки ставится `mcp[cli]`
   (команды `mcp dev`, `mcp run`, `mcp version`). Если переходишь с v1 на v2 — миграция по таблице
   импортов из `../AGENTS.md` §«Стек: только официальный SDK MCP».
2. Модульный `httpx.Client` на процесс: `TESTOPS_TIMEOUT` (по умолчанию 60), `TESTOPS_VERIFY_SSL`,
   `headers` с токеном; ретраи с backoff для `GET/HEAD` на `429` и `5xx` (не более 3 попыток).
3. `_paged(path, **params)` — один разбор конверта `Page*Dto` (`content`, `totalElements`, `totalPages`,
   `number`, `size`), `size` по умолчанию 50, максимум 100.
4. `_guard` — единая обработка ошибок: `{"ok": false, "error": ...}`; `202/204` → `{"ok": true, "accepted": true}`;
   не-JSON при `2xx` → ошибка.
5. `TESTOPS_READ_ONLY` — write-инструменты не регистрируются.
6. **Д1**: `run_test_cases` → `leafsInclude` (и `ids` разбирается в список).
7. **Д2**: `search_test_cases(name=…)` → AQL `name ~ "…"` через `__search`, клиентскую выгрузку удалить.
8. **Д3**: docstring `get_test_case` без обещания шагов + `get_test_case_steps`.
9. Контрактные тесты:
   - `tests/test_contract.py`: каждое тело, собираемое инструментами, валидируется схемой из
     `../openapi/api-docs.json` (`jsonschema`); список тел — не меньше 8 (create/update test case, step,
     test plan, launch, test result, run_test_cases, api_request).
   - `tests/test_client.py`: `httpx.MockTransport` — пагинация, `oneOf` запусков, `202`, `204`, ошибка с `message`.
   - `tests/test_tool_guards.py`: `project_id` без env даёт понятную ошибку; `TESTOPS_READ_ONLY` скрывает write.

**Критерии приёмки:**
- `python -m py_compile src/mcp_testops/*.py` и `pytest -q` зелёные;
- тест, который падает, если вернуть `leafIds` (проверить мутацией: подменить `leafsInclude` → `leafIds`);
- `TESTOPS_READ_ONLY=true python -m mcp_testops` поднимается и не показывает write-инструментов
  (проверяется в тесте по списку зарегистрированных инструментов, а не глазами).

## M2. Полный read-контур

**Цель:** агент может разобраться в проекте, не прибегая к `api_request`.

Задачи:

1. `list_statuses(project_id?, workflow_id?)` — `GET /api/status`.
2. `list_reference(kind, project_id?, query?)` — `workflow | testlayer | custom_field | tag`
   (`/api/workflow`, `/api/testlayer`, `/api/project/{projectId}/cf`, `/api/tag`).
3. `validate_aql(project_id?, rql, deleted)` — `/api/testcase/query/validate`.
4. `get_launch_statistic(launch_id)` — `/api/launch/{id}/statistic`.
5. `get_test_result(test_result_id)` — `/api/testresult/{id}` с белым списком полей.
6. `list_launches`: терпимый разбор `oneOf` (`LaunchDto` и `LaunchPreviewDto`), компактная сводка
   `{id, name, closed, createdDate, statistic}`.
7. Компактные ответы: убрать `*Html`, для листингов — без `indent`.

**Критерии приёмки:**
- сценарий «найти кейсы по тегу → открыть кейс → прочитать шаги → найти прогоны с этим кейсом»
  выполняется без единого `api_request`;
- тест на каждый новый инструмент с записанным ответом (MockTransport), включая форму `LaunchPreviewDto`;
- живой смоук: `list_projects` → `list_reference("workflow", 65)` → `search_test_cases(rql='name ~ "a"')`.

## M3. Write-контур прогонов

**Цель:** агент умеет провести регресс и записать результаты.

Задачи:

1. `create_launch` (расширить: `releaseId`, `tags`, `links`), `close_launch`, `reopen_launch`, `delete_launch`.
2. `add_test_result` с валидацией `TestStatus` **до** запроса.
3. `add_test_case_step` (`ScenarioStepCreateDto`, ровно один из `body`/`attachment_id`/`shared_step_id`).
4. `run_test_cases` — дописать `assignees`, `tags`, `release_id`, `filter_id`/`rql` в `selection`.
5. `update_test_case` — параметр `clear`, чтобы `""` не затирал поля случайно.

**Критерии приёмки:**
- сценарий «создать кейс с тремя шагами → прогнать в новом запуске → записать результат → закрыть запуск»
  проходит целиком на тестовом проекте;
- тесты: тело `TestCaseBulkRunNewLaunchDto` и `ScenarioStepCreateDto` валидируются схемой;
- неверный `status` даёт `{"ok": false, "error": "status must be one of …"}` и **не** ходит в сеть
  (проверяется MockTransport'ом, который считает вызовы);
- удалённые за прогон артефакты: кейс с `force=true`, запуск.

## M4. Эксплуатация и безопасность

**Цель:** сервер не может навредить и не врёт в документации.

Задачи:

1. `api_request` — whitelist методов, denylist префиксов (`/api/project*` для `DELETE`, `/api/account`,
   `/api/mfa`, `/api/admin`, `/api/registration`, `/api/invite`, `/api/integration`, `/api/token`),
   обязательный префикс `/api` без автоподстановки, уважение `TESTOPS_READ_ONLY`.
2. Логи: ни токена, ни заголовков, ни тел ответов; только метод, путь, код, длительность.
3. README: актуальная версия API (`527u04`, дата снятия), проверенная схема авторизации, таблица env,
   пример `opencode.json` с `"TESTOPS_TOKEN": "****"`, раздел «Ограничения» (TLS verify off, read-only).
4. `../AGENTS.md` в репозитории — синхронизировать с этой аналитикой (правила и запреты).
5. Дифф спеки: скрипт/инструкция «как переснять `api-docs` и что смотреть».

**Критерии приёмки:**
- `api_request("DELETE", "/api/project/65")` возвращает ошибку, а не удаляет проект (тест);
- `grep -ri "token" README.md` не находит реального значения;
- README упоминает `527u04` и дату снятия спеки.

## Тестирование

| Уровень | Что | Чем |
|---|---|---|
| Контракт | тела запросов и формы ответов | `jsonschema` + `../openapi/api-docs.json` |
| Поведение | пагинация, `oneOf`, `202/204`, ошибки, ретраи | `httpx.MockTransport` |
| Регресс дефектов | Д1–Д11 | отдельные тесты, которые падают на коде до исправления |
| Живой смоук | чтение на тестовом проекте | вручную/скриптом, отдельно от CI |

Правило: **исправление без теста, который падает до него, не считается исправлением.** Для Д1–Д9
это буквально проверяемо: откатить фикс — тест должен упасть.

## Риски

| Риск | Что делать |
|---|---|
| Спека 527u04 устареет на стенде | переснять `api-docs` перед M2 и сверить `info.version` |
| Авторизация `Api-Token` не подтвердится | вопрос 1 в `06-open-questions.md`; до подтверждения не писать в README как факт |
| Синтаксис AQL неизвестен | `validate_aql` + вопрос 2 |
| `size` больше 100 может не поддерживаться | держать 50, лимит 100; вопрос 6 |
| `202` без известного пути опроса | вопрос 3; до ответа не строить загрузку результатов на 202 |
| TLS verify off | явно в README, не включать по умолчанию `true` без проверки стенда |

## Definition of Done для этапа

- код + тесты зелёные (`pytest -q`, `py_compile`);
- документы в этой папке обновлены, если реализация разошлась с ними;
- README репозитория не противоречит фактам (версия API, схема авторизации, список инструментов);
- коммит(ы) по одной теме, сообщение объясняет «зачем», а не только «что».
