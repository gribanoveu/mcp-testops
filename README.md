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

## MCP-сервер `mcp-testops`

Stdio-сервер MCP поверх API Allure TestOps. Снимок спеки — `openapi/api-docs.json`: `allure-testops-service`
`527u04` (ветка `527u04`), `info.version` = `527u04`, снято **2026-11-09**. Стек — официальный SDK `mcp`
v2 (`MCPServer` из `mcp.server`, проверено на 2.3.0) и `httpx`; транспорт stdio, портов сервер не слушает.

**30 инструментов: 17 read + 13 write.** Generic-инструмента «любой путь под `/api`» нет сознательно:
чего не хватает, добавляется именованным инструментом с телом из схемы (`docs/03-tools-spec.md` §7).

### Установка и запуск

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[test]" "mcp[cli]"             # mcp[cli] — команды mcp dev / mcp run / mcp version
python -m mcp_testops                          # stdio; без TESTOPS_TOKEN падает с понятным сообщением
```

### Переменные окружения

| Переменная | Обязательна | По умолчанию | Смысл |
|---|---|---|---|
| `TESTOPS_TOKEN` | да | — | API-токен; без него старт прерывается с `TESTOPS_TOKEN is not set` |
| `TESTOPS_BASE_URL` | нет | `https://testops.moscow.alfaintra.net` | хост стенда |
| `TESTOPS_PROJECT_ID` | нет | — | проект по умолчанию для инструментов без `project_id` |
| `TESTOPS_VERIFY_SSL` | нет | `false` | проверка TLS; внутренний стенд на самоподписанном CA |
| `TESTOPS_TIMEOUT` | нет | `60` | таймаут запроса, секунды |
| `TESTOPS_READ_ONLY` | нет | `false` | `true` — регистрируются только read-инструменты (17 из 30) |
| `MCP_SERVER_NAME` | нет | `testops` | имя сервера в клиенте |

### Подключение клиента (пример)

Форма блока `mcp` — как в вашем клиенте; ниже — локальный сервер, который клиент запускает подпроцессом.
Токен в конфиг попадает только реальным значением в локальном файле, в репозиторий — никогда:

```json
{
  "mcp": {
    "testops": {
      "type": "local",
      "command": ["python", "-m", "mcp_testops"],
      "environment": {
        "TESTOPS_BASE_URL": "https://testops.moscow.alfaintra.net",
        "TESTOPS_TOKEN": "****",
        "TESTOPS_PROJECT_ID": "65",
        "TESTOPS_READ_ONLY": "true"
      }
    }
  }
}
```

### Инструменты

| Домен | Инструменты |
|---|---|
| Проекты | `list_projects`, `get_project` |
| Кейсы | `list_test_cases`, `get_test_case`, `get_test_case_steps`, `get_test_case_history`, `search_test_cases`, `validate_aql`, `create_test_case`, `update_test_case`, `delete_test_case`, `add_test_case_step` |
| Тест-планы | `list_test_plans`, `get_test_plan`, `create_test_plan`, `update_test_plan`, `delete_test_plan` |
| Запуски и результаты | `list_launches`, `get_launch`, `get_launch_statistic`, `list_test_results`, `get_test_result`, `create_launch`, `close_launch`, `reopen_launch`, `delete_launch`, `add_test_result`, `run_test_cases` |
| Справочники | `list_statuses`, `list_reference` |

Сигнатуры, тела и что инструмент возвращает — `docs/03-tools-spec.md`. Ответы компактные: HTML-дубли
(`*Html`) вырезаны, листинги без `indent`.

### Ограничения и риски

- **Авторизация не подтверждена спекой:** в снимке нет `security`/`securitySchemes`; используется
  `Authorization: Api-Token <token>` — допущение (`docs/06-open-questions.md`, вопрос 1). При 401/403
  первым делом проверить, не нужен ли `Bearer`.
- **`TESTOPS_VERIFY_SSL=false` по умолчанию** — осознанное послабление для самоподписанного CA: TLS
  не проверяется. На стенде с валидным сертификатом выставлять `true`.
- **`TESTOPS_READ_ONLY`** скрывает 13 write-инструментов из 30; на рабочем проекте включать явно.
- **Нет generic-вызова и загрузки файлов:** дерево, общие шаги, дефекты, вложения и импорт результатов
  через MCP недоступны; для вложений и архивов нужен отдельный именованный инструмент (multipart
  JSON-строкой не собрать).
- **Удаление кейса — мягкое:** `DELETE /api/testcase/{id}` отвечает `202` и, судя по схеме, уводит кейс в
  корзину; восстановление не выведено (`docs/06-open-questions.md`, вопрос 8).
- **Логи:** только метод, путь, код и длительность; токен, заголовки и тела не пишутся. Логгер `httpx`
  при старте сервера приглушён — он сыплет полными URL вместе с текстом `rql`.
- **Аналитика в `docs/`** могла устареть относительно кода — источник правды `openapi/api-docs.json`
  и контрактные тесты.

### Проверка и разработка

```bash
python -m py_compile src/mcp_testops/*.py src/mcp_testops/tools/*.py
pytest -q                                        # 68 тестов: контракт, MockTransport, гарды
mcp version                                      # версия официального SDK
mcp dev src/mcp_testops/__init__.py              # Inspector: что увидит модель
python -m mcp_testops                            # stdio, читает TESTOPS_* из env
```

Переснять снимок спеки перед этапом и посмотреть дифф:

```bash
scripts/refresh_spec.sh          # curl /api-docs/ в openapi/api-docs.json.new + дифф путей и схем
```

Скрипт не перезаписывает `openapi/api-docs.json`: сначала читаются версия и дифф, потом снимок меняется
и гоняются `pytest -q`. Подробнее — `docs/06-open-questions.md`, вопрос 10.

Что сделано на каждом этапе — `CHANGELOG.md`.
