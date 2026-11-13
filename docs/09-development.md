# Разработка и проверка

## Проверки перед сдачей

```bash
python -m py_compile src/mcp_testops/*.py src/mcp_testops/tools/*.py
pytest -q                                        # 63 теста: 62 passed, 1 skipped
mcp version                                      # версия официального SDK
mcp dev src/mcp_testops/__init__.py              # Inspector: что увидит модель
python -m mcp_testops                            # stdio, читает TESTOPS_* из env
```

`mcp dev` — самый быстрый способ увидеть схему аргументов инструмента: Inspector показывает ровно то,
что получит модель.

`pytest -q` без снимка спеки даёт 62 passed и 1 skipped: `tests/test_contract.py` помечается skipped,
когда нет `openapi/api-docs.json`.

## Снимок спеки

```bash
scripts/refresh_spec.sh          # curl /api-docs/ в openapi/api-docs.json.new + дифф путей и схем
```

Скрипт не перезаписывает `openapi/api-docs.json`: сначала печатаются `info.version` и дифф путей и
схем, потом снимок меняется вручную и гоняются тесты. Полного снимка в репозитории нет — каждый берёт
его со своего стенда. В `openapi/` лежат только выборки: `api-inventory.md` (пути по тегам) и
`key-schemas.json` (схемы, нужные инструментам).

## Контрактные тесты

`tests/test_contract.py` валидирует собранные тела запросов схемами из снимка и разобранные ответы —
существующими схемами. Это ловит дефекты класса «поле называется иначе»: именно так в чужом примере
был сломан `run_test_cases` (разбор — `docs/04-current-implementation.md`).

`tests/test_client.py` гоняет инструменты на `httpx.MockTransport`: пагинация, `oneOf`, `202`/`204`,
ошибки, AQL, шаги, фильтры. `tests/test_tool_guards.py` — `project_id`, `TESTOPS_READ_ONLY` и
отсутствие generic-инструмента.

## Standalone-бинарник

То же, что делает релизный workflow:

```bash
pip install -e ".[build]"
pyinstaller --onefile --name mcp-testops --distpath dist-bin --workpath build/pyi \
  --collect-submodules mcp.server --collect-all pydantic --collect-all anyio \
  --hidden-import mcp_testops packaging/entry.py
```

`--collect-submodules mcp.server`, а не `--collect-all mcp`: последний обходит `mcp.cli`, которому
нужен `typer` из экстры `mcp[cli]`, и сборка падает на `ModuleNotFoundError: No module named 'typer'`.

Проверка собранного: запустить без `TESTOPS_TOKEN` — должен выйти с кодом 1 и напечатать
`TESTOPS_TOKEN is not set`. То же проверяет смоук-шаг релизного workflow.

## Публикация

Тег `vX.Y.Z` запускает `.github/workflows/release.yml`: тесты, колесо и sdist, четыре бинарника,
затем релиз на GitHub и npm.

- Версия живёт в трёх местах и должна совпадать: `pyproject.toml`, `npm/package.json`, ссылка на колесо
  в README. Релизный workflow сверяет тег с `npm/package.json` и падает при расхождении.
- **npm идёт по trusted publishing (OIDC):** job просит `id-token: write`, у `setup-node` нет
  `registry-url` (он писал бы `_authToken` и ломал OIDC), `NODE_AUTH_TOKEN` не передаётся вовсе.
  Схема двухшаговая: `npm stage publish` в CI, затем мейнтейнер с 2FA одобряет
  `npm stage approve <stage-id>` (или на npmjs.com). Команда `stage` есть только в npm 12 — job ставит
  его поверх node 24.
- **Скилл едет в npm-пакете:** `npm/copy-skill.js` на `prepack` копирует `skills/testops-mcp/` внутрь
  пакета (копия в git не попадает), поэтому `npx -y @gribanoveu/mcp-testops skill` раскладывает
  `SKILL.md` и `aql.md` у клиента.
- **PyPI** — `.github/workflows/publish-pypi.yml`, trusted publishing с environment `pypi`; job помечен
  `continue-on-error`, пока проект на PyPI не создан: падение не валит прогон релиза.
- Каталог Kibo Agent (`gribanoveu/kibo-agent-catalog`) держит записи `testops` (MCP) и `testops-mcp`
  (скилл); при изменении скилла поднимайте там `rev`, иначе установленным копиям не предложат обновление.

## Структура

```
testops-mcp/
├── src/mcp_testops/
│   ├── __init__.py       # импорт модулей инструментов (регистрация) + main()
│   ├── __main__.py       # from . import main; main()
│   ├── config.py         # TESTOPS_* из env, размеры страниц, ретраи, enum'ы
│   ├── client.py         # TestOpsError, httpx-клиент, _send/_api/_paged, логи
│   ├── helpers.py        # guard, разбор аргументов, компактность ответа
│   ├── bodies.py         # тела запросов — чистые функции для контрактных тестов
│   ├── server.py         # mcp = MCPServer(...) и _write (read-only)
│   └── tools/            # проекты, кейсы, планы, запуски, справочники
├── tests/                # test_contract.py, test_client.py, test_tool_guards.py
├── scripts/refresh_spec.sh   # получить снимок спеки со стенда
├── scripts/call.py           # вызвать любой инструмент из терминала
├── openapi/              # выборки из спеки: api-inventory.md, key-schemas.json
├── docs/                 # аналитика (01–06) и справочники (07–09)
├── packaging/entry.py    # точка входа для standalone-бинарника
├── npm/                  # обёртка и скилл в npm-пакете
├── skills/testops-mcp/   # SKILL.md для агента и aql.md с референсом AQL
├── AGENTS.md             # правила работы над сервером
├── CHANGELOG.md          # что сделано, по этапам
├── README.md             # как поставить и подключить
└── pyproject.toml        # hatchling, mcp>=2,<3, httpx
```

## Вызов инструментов из терминала

`scripts/call.py` поднимает сервер по stdio так же, как клиент, и печатает ответ инструмента — то,
что увидит модель:

```bash
export TESTOPS_TOKEN=... TESTOPS_BASE_URL=https://testops.net TESTOPS_PROJECT_ID=657
python scripts/call.py --list                                  # 30 инструментов и первые строки docstring
python scripts/call.py --schema list_launches                  # схема аргументов
python scripts/call.py list_projects '{"search": "wowtax"}'     # вызов, аргументы — JSON-объект
```

Запускать из окружения пакета (`.venv/bin/python`) — скрипт импортирует SDK `mcp`. Код возврата — `0`,
если инструмент ответил; `1` — когда ответ получен на уровне протокола как ошибка (например,
пропущен обязательный аргумент) или аргументы не разбираются как JSON. Наш стиль «ошибки — данные» это
не меняет: `{"ok": false, "error": "HTTP 403 ..."}` — это ответ, и код возврата `0`, разбирать надо
поле `error`.

Два подводных камня, из-за которых скрипт выглядит именно так:

- `anyio.run`, а не `asyncio.run`: stdio-транспорт SDK строит anyio task group, и под `asyncio.run` её
  закрытие падает с `ExceptionGroup` уже после печати ответа (Python 3.14, anyio 4).
- поля SDK — snake_case: `tool.input_schema`, `result.is_error` (не `inputSchema`/`isError`).

Вместо скрипта можно и голым JSON-RPC — сервер читает stdin и пишет stdout:

```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"cli","version":"1"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
 | TESTOPS_TOKEN=dummy python -m mcp_testops
```

## Правила кода

Они в `AGENTS.md`: одна функция — один инструмент, docstring как контракт для модели, сложные
аргументы JSON-строкой, ошибки как данные, компактные ответы, один HTTP-клиент на процесс, пагинация в
одном месте, мутации уважают `TESTOPS_READ_ONLY`.
