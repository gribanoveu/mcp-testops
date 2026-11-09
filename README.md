# MCP-сервер для Allure TestOps — аналитика для реализации

Пакет документов, по которому агент-исполнитель (или человек) делает MCP-сервер для Allure TestOps
Альфа-Банка: контракт API, модель данных, спецификация инструментов, разбор примера, план работ и
открытые вопросы. Код пишется **в этой же папке** — больше никуда ходить не нужно.

## Источник данных

| Что | Значение |
|---|---|
| Спецификация | `GET https://testops.moscow.alfaintra.net/api-docs/` |
| Снята | 2026-11-09, ответ 200, `application/json`, 738 020 байт |
| Формат | OpenAPI 3.1.0 |
| Сервис | `allure-testops-service`, версия `527u04` (ветка `527u04`, коммит `98b8eafc39cede7ab290218df82031c732afd2dc`) |
| Объём | 634 пути, 845 операций, 176 тегов, 803 схемы |
| Где ведётся работа | эта папка `testops-mcp/`: здесь аналитика, здесь же появляется код и тесты |
| Пример (только чтение) | `reference/` — фрагменты `MMBMB/mcp-testops` (HEAD `ad9c4daa`, снято 2026-11-09); внешний репозиторий в работе не участвует |

Снимок спецификации лежит рядом — `openapi/api-docs.json`. Всё, что написано в документах,
проверено по нему; всё, что проверено не было, помечено как открытый вопрос (`docs/06-open-questions.md`).

## Состав

| Файл | Кому и зачем |
|---|---|
| `AGENTS.md` | правила работы: конвенции, что нельзя, как проверять, как поднять каркас в этой папке |
| `CHANGELOG.md` | строка на этап: что сделано и когда |
| `docs/01-contract.md` | как устроен API: авторизация, пагинация, ошибки, AQL, полиморфные ответы |
| `docs/02-domain-model.md` | сущности и связи: Project → TestCase → TestPlan → Launch → TestResult, справочники, дерево |
| `docs/03-tools-spec.md` | **главный документ**: 30 инструментов — сигнатура, эндпоинт, тело, ответ, ошибки |
| `docs/04-current-implementation.md` | разбор примера из `reference/`: решения, ошибки (Д1–Д11) с номерами строк — читать как «чего не делать» |
| `docs/05-plan.md` | этапы M0–M4, критерии приёмки, стратегия тестирования |
| `docs/06-open-questions.md` | что проверить на стенде до/во время реализации |
| `openapi/api-docs.json` | снимок спецификации — источник контрактных тестов |
| `openapi/api-inventory.md` | все 845 операций по префиксам: метод, путь, summary, тег |
| `openapi/key-schemas.json` | 98 схем, нужных инструментам (запросы, ответы, enum'ы), с замыканием по `$ref` |
| `reference/` | пример чужой реализации, сохранённый в папку: `README.md` (происхождение) и `skeleton-excerpt.md` (код с номерами строк) |
| `src/mcp_testops/`, `tests/` | код сервера и тесты; `pyproject.toml` — сборка (hatchling) и зависимости |

## Порядок чтения

1. `AGENTS.md` — правила.
2. `docs/04-current-implementation.md` — какие решения примера стоит перенять и какие повторять нельзя.
3. `docs/03-tools-spec.md` — что писать.
4. `docs/01-contract.md` + `docs/02-domain-model.md` — детали контракта по месту.
5. `docs/05-plan.md` — в каком порядке и когда считать готовым.

## Коротко о главном

- Стек — **только официальный MCP Python SDK `mcp`** (`MCPServer` из `mcp.server` в v2, `FastMCP` в v1),
  без сторонних фреймворков; транспорт stdio; HTTP — `httpx`. Детали и команды — `AGENTS.md`,
  раздел «Стек: только официальный SDK MCP».

- Спецификация не описывает авторизацию (`security`/`securitySchemes` отсутствуют), фактически используется
  `Authorization: Api-Token <token>`. Это допущение, его надо подтвердить на стенде.
- API — Spring Data: `page`/`size`/`sort`, ответы `Page*Dto` с `content`/`totalElements`/`totalPages`.
  `size` по умолчанию 10.
- Фильтрация — AQL, в API называется `rql`: `GET /api/testcase/__search?projectId&rql`, проверка —
  `GET /api/testcase/query/validate`.
- `TestCaseDto` **не содержит сценария** — шаги читаются `GET /api/testcase/{id}/step`.
- В примере из `reference/` `run_test_cases` собирает поле `leafIds`, которого в схеме нет (нужно
  `leafsInclude`), поэтому прогон создаётся пустым — эту ошибку не повторять.
- Никакого внешнего репозитория: работа и коммиты — там, где лежит эта папка. `reference/` —
  снимок примера для чтения, он может устареть и не обновляется.

## Проект в этой папке (M0–M1)

Каркас поднят рядом с аналитикой: `pyproject.toml`, `src/mcp_testops/`. Линия SDK — **v2**:
`mcp>=2,<3`, `from mcp.server import MCPServer`; проверено на `mcp` 2.3.0. HTTP — `httpx`.

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[test]" "mcp[cli]"             # mcp[cli] — команды mcp dev / mcp run / mcp version
python -m mcp_testops                          # stdio; без TESTOPS_TOKEN падает с понятным сообщением
```

Переменные окружения, таблица инструментов и ограничения — в `docs/01-contract.md` §3 и `docs/03-tools-spec.md`;
полный README пакета появляется в M4. Тесты — `pytest -q` (сейчас 66); линия SDK v2 зафиксирована
в `pyproject.toml`. Что сделано на каждом этапе — `CHANGELOG.md`.
