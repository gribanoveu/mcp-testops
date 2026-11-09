# Changelog

Что сделано, по этапам из `docs/05-plan.md`: одна строка на этап, новое — сверху.

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

## 2026-11-09 — M0. Каркас пакета

- Поднят каркас `mcp-testops` на официальном SDK `mcp` v2 (`MCPServer` из `mcp.server`, проверено
  на 2.3.0): `pyproject.toml` (hatchling, `mcp>=2,<3`, `httpx>=0.27`, тестовые `pytest`/`jsonschema`),
  `src/mcp_testops/`. Без `TESTOPS_TOKEN` запуск падает с `TESTOPS_TOKEN is not set`, с токеном сервер
  отвечает на `initialize` по stdio.
- Аналитика переехала в `docs/` (01–06), перекрёстные ссылки поправлены; правила для агентов остаются
  в `AGENTS.md` в корне.
