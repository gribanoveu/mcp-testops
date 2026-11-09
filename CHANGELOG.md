# Changelog

Что сделано, по этапам из `docs/05-plan.md`: одна строка на этап, новое — сверху.

## 2026-11-09 — M3. Write-контур

- `delete_test_case(force)` (`DELETE` + `202`), `update_test_plan` (тело `TestPlanPatchDto`, `clear` как в
  `update_test_case`), `delete_test_plan` (`204`), `close_launch`/`reopen_launch` (`204`),
  `delete_launch` (`204`). Все шесть собирают ответ через `_answer`, поэтому `accepted` от 202/204 видно
  модели.
- Тело патча теперь собирает общий `_patch_body` — раньше он был `_test_case_patch_body` и годился
  только названием для кейсов; `TestPlanPatchDto` валидируется тем же тестом.
- Набор закрыт: 30 инструментов (17 read + 13 write), в `TESTOPS_READ_ONLY=true` — 17; тестов 66.
- Живой смоук «кейс → 3 шага → запуск → результат → close → удалить с force=true» не прогнан: токена стенда
  нет, всё проверено `MockTransport`.

## 2026-11-09 — M2. История прогонов кейса

- Добавлен 30-й инструмент `get_test_case_history` (`GET /api/testcase/history`): по id кейса отдаёт
  строки `{testResultId, launchId, launchName, status, start, stop, duration, message, testedBy}`;
  `launch` из схемы (`IdAndNameOnlyDto`) разворачивается в поля строки.
- Закрыт вопрос 13: сценарий M2 теперь выполним целиком — `search_test_cases` → `get_test_case` →
  `get_test_case_steps` → `get_test_case_history` → `get_test_result`.
- Набор: 24 инструмента (17 read + 7 write), в `TESTOPS_READ_ONLY=true` — 17. Тестов 60.

## 2026-11-09 — M2. Read-контур закрыт

- `validate_aql` — проверка AQL до поиска: `{valid, count}`; пустой `rql` — ошибка без запроса.
- `get_launch_statistic` — массив `TestStatusCount` → `{status: count}`, один запрос вместо листания
  результатов.
- `get_test_result` — белый список полей `TestResultDto` без `*Html`-дублей.
- Найдено при сверке критериев M2: «в каких прогонах гонялся кейс» не отвечается ни одним из 29
  инструментов — нужен `GET /api/testcase/history`, такого инструмента нет. Вопрос 13 в
  `docs/06-open-questions.md`, критерий M2 в `docs/05-plan.md` переписан честно.
- Итог: 23 инструмента (16 read + 7 write), в `TESTOPS_READ_ONLY=true` — 16. Тестов 59.

## 2026-11-09 — M1.5. Generic-инструмент убран, справочники добавлены

- `api_request` удалён из сервера целиком. Денилист по принципу «разрешено всё, что не перечислено»
  пропускал `POST /api/register` (в спеке нет `/api/registration`), обход через `%61ccount` и `..`
  требовал нормализации пути, а `POST /api/testcase/bulk/remove` проходил без валидации тела.
  Правило «не возвращать» — `docs/03-tools-spec.md` §7 и `AGENTS.md`; набор держит закрытым тест
  `test_no_generic_escape_hatch`.
- Без generic-вызова id статуса стало неоткуда брать, поэтому сразу появились справочники:
  `list_statuses` (`GET /api/status`; у эндпоинта нет `projectId` — статусы задаются workflow) и
  `list_reference` (`workflow`, `testlayer`, `custom_field`, `tag`; `tag` — плоский массив, `query`
  фильтруется на клиенте). Оба с тестами на путь, параметры и компактный ответ.
- Итог: 20 инструментов (13 read + 7 write), в `TESTOPS_READ_ONLY=true` — 13. Из 29 по спеке остались
  `validate_aql`, `get_launch_statistic`, `get_test_result` (M2) и шесть write (M3).

## 2026-11-09 — M1. Клиент, контрактные тесты, критические исправления

- Один `httpx.Client` на процесс (`TESTOPS_TIMEOUT`, `TESTOPS_VERIFY_SSL`, заголовок `Api-Token`),
  ретраи с backoff до 3 попыток только для `GET`/`HEAD` на `429`/`5xx`; `_paged` — единый разбор
  `Page*Dto` (`size` 50, потолок 100); `_guard` — ошибки данными, `202`/`204` дают `{ok, accepted}`,
  не-JSON при `2xx` — ошибка.
- `TESTOPS_READ_ONLY=true` снимает с регистрации 7 write-инструментов (проверено: 19 инструментов по
  stdio, 12 в read-only); `api_request` остаётся ради `GET`.
- 19 инструментов: проекты, кейсы, шаги, тест-планы, запуски, результаты, `api_request`.
  `run_test_cases` собирает `leafsInclude` (Д1), `search_test_cases(name=…)` идёт в `__search` с
  `name ~ "…"` без клиентской выгрузки (Д2), `get_test_case` отвечает `steps_not_included` и есть
  `get_test_case_steps` (Д3), `update_test_case` получил `clear` (Д8).
- Тесты: 36 штук — тела запросов валидируются схемами из `openapi/api-docs.json`, поведение клиента
  на `MockTransport` (пагинация, обе формы запусков, `202`/`204`, ошибки, ретраи), гарды (`project_id`,
  read-only, запреты `api_request`). Возврат `leafIds` валит тест — проверено мутацией.
- Спека: `TestCaseScenarioV2Dto.steps` невалидируем (`oneOf` из четырёх DTO без различителя по `type`),
  в `TestCaseTreeSelectionDto` нет поля `rql` — оба факта в `docs/06-open-questions.md` (5 и 12), спека
  инструментов в `docs/03-tools-spec.md` приведена к коду.

### M1, ревью

- `api_request`: в денилисте стоял несуществующий `/api/registration` — регистрация в спеке это
  `POST /api/register`, то есть учётку можно было создать. Добавлены `/api/register`,
  `/api/globalsettings/mfa`, `/api/email-verification`, `/api/login/invite-personal`; путь перед
  проверками раскодируется и нормализуется, иначе `/api/%61ccount/1` и `/api/./account/1` обходили список.
- `202` с телом больше не теряется: `_api` отдаёт тело вместе с `accepted`, write-инструменты собирают
  ответ через `_answer`, поэтому `launchId`/`createdStepId` не приходят `null` и «принято асинхронно»
  отличимо от «создано».
- Docstring'и сверены со схемами: `MemberDto.role` — объект `RoleDto`, `CustomFieldDto` требует `id` и
  `name`, у `TreeSelectionDto` нет `filterId`, `update_test_case` получил `members_json` и
  `scenario_json`, `add_test_result` описал свои JSON-аргументы, `create_test_case` больше не ссылается
  на инструменты M2.
- `search_test_cases` экранирует кавычки в `name`; `_statistic` для объекта отдаёт ключи как есть
  (`StatisticDto`: `inProgress`, `pending`, `total`); `get_test_case_steps` сам находит корни, если
  `root` не пришёл — раньше вернулось бы ложное «шагов нет».
- Тесты: 62 вместо 36 — тела write-инструментов сверяются с отправленным запросом, проверены `_http()`
  (один клиент, `Api-Token`, таймаут), исчерпание ретраев, транспортная ошибка, `202` с телом, ответ
  без конверта, все 10 запрещённых префиксов, четыре метода в read-only, `main()` без токена и точный
  набор инструментов в обоих режимах; фикстура `api` падает, если хендлер не установлен.

## 2026-11-09 — M0. Каркас пакета

- Поднят каркас `mcp-testops` на официальном SDK `mcp` v2 (`MCPServer` из `mcp.server`, проверено
  на 2.3.0): `pyproject.toml` (hatchling, `mcp>=2,<3`, `httpx>=0.27`, тестовые `pytest`/`jsonschema`),
  `src/mcp_testops/`. Без `TESTOPS_TOKEN` запуск падает с `TESTOPS_TOKEN is not set`, с токеном сервер
  отвечает на `initialize` по stdio.
- Аналитика переехала в `docs/` (01–06), перекрёстные ссылки поправлены; правила для агентов остаются
  в `AGENTS.md` в корне.
