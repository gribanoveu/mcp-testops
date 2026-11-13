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
│   ├── cli.py            # python -m mcp_testops call … (один вызов из терминала)
│   └── tools/            # проекты, кейсы, планы, запуски, справочники
├── tests/                # test_contract.py, test_client.py, test_tool_guards.py, test_cli.py
├── scripts/refresh_spec.sh   # получить снимок спеки со стенда
├── openapi/              # выборки из спеки: api-inventory.md, key-schemas.json
├── docs/                 # аналитика (01–06) и справочники (07–09)
├── packaging/entry.py    # точка входа для standalone-бинарника
├── npm/                  # обёртка и оба скилла в npm-пакете
├── skills/testops-mcp/   # скилл для MCP-сервера: SKILL.md + aql.md
├── skills/testops-cli/   # тот же домен командами CLI: SKILL.md + aql.md
├── AGENTS.md             # правила работы над сервером
├── CHANGELOG.md          # что сделано, по этапам
├── README.md             # как поставить и подключить
└── pyproject.toml        # hatchling, mcp>=2,<3, httpx
```

## Вызов инструментов из терминала

`python -m mcp_testops call …` — штатная подкоманда (`cli.py`), не отдельный скрипт: она поднимает сервер
по stdio так же, как клиент, делает один вызов и печатает ответ:

```bash
export TESTOPS_TOKEN=... TESTOPS_BASE_URL=https://testops.net TESTOPS_PROJECT_ID=657
python -m mcp_testops call --list                                  # 30 инструментов + первая строка docstring
python -m mcp_testops call --schema list_launches                  # схема аргументов
python -m mcp_testops call list_projects '{"search": "wowtax"}'    # вызов, аргументы — JSON-объект
```

Та же команда через npm-обёртку — она передаёт аргументы бинарнику как есть, подкоманда ему знакома
с 0.2.0: `npx -y @gribanoveu/mcp-testops call --list`. Для замороженного бинарника `_self_command()`
поднимает его самого без `-m` — PyInstaller не понимает `-m mcp_testops`.

stdout — только ответ инструмента, логи идут в stderr, так что stdout можно пайпить в `jq`. Код
возврата `0` — инструмент ответил (даже если внутри `{"ok": false, "error": …}`), `1` — ошибка
уровня протокола (пропущен обязательный аргумент) или аргументы не JSON.

Два подводных камня, которые видны в `cli.py`:

- `anyio.run`, а не `asyncio.run`: stdio-транспорт SDK строит anyio task group, и под `asyncio.run` её
  закрытие падает с `ExceptionGroup` уже после печати ответа (Python 3.14, anyio 4);
- поля SDK — snake_case: `tool.input_schema`, `result.is_error` (не `inputSchema`/`isError`).

Тесты — `tests/test_cli.py`: они запускают подпроцесс так же, как это делает человек, и ни один из
случаев не идёт в сеть.

Голым JSON-RPC тоже можно — сервер читает stdin и пишет stdout:

```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2026-07-28","capabilities":{},"clientInfo":{"name":"cli","version":"1"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
 | TESTOPS_TOKEN=dummy python -m mcp_testops
```

## Два скилла: сервер или CLI

- `skills/testops-mcp` — для тех, кто регистрирует MCP-сервер: рецепты вызовов инструментов.
- `skills/testops-cli` — тот же домен, но командами `python -m mcp_testops call …` через shell, без
  регистрации сервера. Плата за это: 30 описаний инструментов (29 143 символа в `tools/list`) не лежат
  в контексте постоянно; цена — модель не видит схем и берёт имена аргументов из скилла.

Оба ставит `mcp-testops skill [testops-mcp|testops-cli] [--all] [--dir …] [-g]`, а `aql.md` в них —
один и тот же файл.

## Правила кода

Они в `AGENTS.md`: одна функция — один инструмент, docstring как контракт для модели, сложные
аргументы JSON-строкой, ошибки как данные, компактные ответы, один HTTP-клиент на процесс, пагинация в
одном месте, мутации уважают `TESTOPS_READ_ONLY`.
