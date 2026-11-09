# mcp-testops — MCP-сервер для Allure TestOps

MCP-сервер (stdio) поверх API Allure TestOps: проекты, тест-кейсы с шагами, тест-планы, запуски и
результаты, справочники. Написан на **официальном Python SDK `mcp` v2** (`MCPServer` из `mcp.server`,
проверено на `mcp` 2.3.0) и `httpx`; транспорт — stdio, сервер не слушает портов и запускается
клиентом подпроцессом.

**30 инструментов: 17 read + 13 write.** Generic-инструмента «любой путь под `/api`» нет сознательно:
чего не хватает, добавляется именованным инструментом с телом из схемы — почему именно так,
в `docs/03-tools-spec.md` §7.

Контракт — API `allure-testops-service` `527u04`, снимок от 2026-11-09 (634 пути, 845 операций, 803 схемы).
Полного снимка в репозитории нет: `scripts/refresh_spec.sh` получает его с вашего стенда в
`openapi/api-docs.json`, и тогда контрактные тесты сверяют по нему тела запросов и формы ответов.
Лицензия — MIT (`LICENSE`).

## Инструменты

| Домен | Инструменты |
|---|---|
| Проекты | `list_projects`, `get_project` |
| Тест-кейсы | `list_test_cases`, `get_test_case`, `get_test_case_steps`, `get_test_case_history`, `search_test_cases`, `validate_aql`, `create_test_case`, `update_test_case`, `delete_test_case`, `add_test_case_step` |
| Тест-планы | `list_test_plans`, `get_test_plan`, `create_test_plan`, `update_test_plan`, `delete_test_plan` |
| Запуски и результаты | `list_launches`, `get_launch`, `get_launch_statistic`, `list_test_results`, `get_test_result`, `create_launch`, `close_launch`, `reopen_launch`, `delete_launch`, `add_test_result`, `run_test_cases` |
| Справочники | `list_statuses`, `list_reference` |

Что стоит знать до первого вызова:

- API называет AQL полем `rql`. `search_test_cases(name=...)` превращает имя в запрос `name ~ "…"` на
  сервере; `validate_aql` проверяет запрос до поиска и отдаёт `{valid, count}`.
- `TestCaseDto` не содержит сценария — шаги читаются `get_test_case_steps`.
- `get_test_case_history` отвечает на «в каких прогонах гонялся этот кейс».
- `run_test_cases` выбирает кейсы через `ids`/`leafs_include` (`selection.leafsInclude`) или сохранённый
  `filter_id`; поля `rql` в выборке нет.
- Сложные аргументы — JSON-строкой: `tags_json`, `links_json`, `custom_fields_json`, `scenario_json`,
  `tree_selection_json`. Примеры — в docstring каждого инструмента.
- Ответы компактные: HTML-дубли текстов (`*Html`) вырезаны, листинги без отступов и с
  `totalElements`/`totalPages`/`number`.
- Ошибки — данные: `{"ok": false, "error": "HTTP 404 on GET /api/testcase/1: …"}` вместо исключения.

## Установка

Четыре пути: npm (без установки или глобально), uv, готовый бинарник, пакет Python.

### 1. Через npm

Пакет опубликован: [`@gribanoveu/mcp-testops`](https://www.npmjs.com/package/@gribanoveu/mcp-testops). Нужен
Node 18+, Python не нужен: при первом запуске обёртка скачивает бинарник своей платформы (22–40 МБ) из
этого же Release в `~/.cache/mcp-testops/` и дальше запускает его оттуда.

```bash
npx -y @gribanoveu/mcp-testops          # без установки: скачает, запустит и закеширует
npm install -g @gribanoveu/mcp-testops  # глобально: в PATH появляется команда mcp-testops
mcp-testops                             # то же самое, без npx на каждый запуск
npx -y @gribanoveu/mcp-testops@0.1.5    # закрепить версию — тем же способом обновляются
```

Всё служебное обёртка пишет в stderr (в том числе строку о загрузке бинарника при первом запуске),
stdout остаётся протоколу MCP.

### 2. Через uv

```bash
uvx --from git+https://github.com/gribanoveu/mcp-testops mcp-testops   # из репозитория, работает сейчас
uvx mcp-testops                                                       # после публикации в PyPI
```

`uvx` собирает пакет в кеш и запускает; нужен только [uv](https://docs.astral.sh/uv/).

### 3. Бинарник из Releases

Скачайте файл под свою систему из [Releases](https://github.com/gribanoveu/mcp-testops/releases),
распакуйте и сделайте исполняемым (macOS/Linux):

```bash
chmod +x mcp-testops-<platform>
./mcp-testops-<platform>          # без TESTOPS_TOKEN — exit 1 и понятное сообщение
```

| Система | Файл ассета |
|---|---|
| macOS Apple Silicon | `mcp-testops-darwin-arm64` |
| Linux x86_64 | `mcp-testops-linux-x64` |
| Linux arm64 | `mcp-testops-linux-arm64` |
| Windows x86_64 | `mcp-testops-win32-x64.exe` |

Для Intel Mac готового бинарника нет: сборка под x64 на раннере GitHub падает на несовпадении OpenSSL
в `cryptography`. На Intel Mac ставьте колесо (пункт 4) или используйте `uvx mcp-testops`.

### 4. Пакет Python

Нужен Python 3.10+. Колесо `py3-none-any` — одно на все платформы:

```bash
pip install https://github.com/gribanoveu/mcp-testops/releases/download/v0.1.5/mcp_testops-0.1.5-py3-none-any.whl
python -m mcp_testops
```

Или из исходников (для разработки, с тестами и CLI-командами SDK):

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[test]" "mcp[cli]"             # mcp[cli] — mcp dev / mcp run / mcp version
python -m mcp_testops                          # stdio; без TESTOPS_TOKEN падает с понятным сообщением
```

> Что уже опубликовано: npm — 0.1.5, в registry.npmjs.org. PyPI пока нет, поэтому `uvx mcp-testops` без
> `--from` ещё не работает: нужен проект `mcp-testops` и trusted publisher для
> `.github/workflows/publish-pypi.yml`. Публикация в npm двухшаговая: workflow ставит версию в очередь
> (`npm stage publish`), мейнтейнер с 2FA одобряет её (`npm stage approve <stage-id>`).

## Настройка

Всё, что зависит от стенда и проекта, приходит из окружения — один пакет поднимается под разные проекты.

| Переменная | Обязательна | По умолчанию | Смысл |
|---|---|---|---|
| `TESTOPS_TOKEN` | да | — | API-токен; без него старт прерывается с `TESTOPS_TOKEN is not set` |
| `TESTOPS_BASE_URL` | нет | `https://testops.net` | хост стенда |
| `TESTOPS_PROJECT_ID` | нет | — | проект по умолчанию для инструментов без `project_id` |
| `TESTOPS_VERIFY_SSL` | нет | `false` | проверка TLS; внутренний стенд на самоподписанном CA |
| `TESTOPS_TIMEOUT` | нет | `60` | таймаут запроса, секунды |
| `TESTOPS_READ_ONLY` | нет | `false` | `true` — регистрируются только read-инструменты (17 из 30) |
| `MCP_SERVER_NAME` | нет | `testops` | имя сервера в клиенте |

## Подключение в Cursor

Cursor читает MCP-серверы из `mcp.json`: глобально — `~/.cursor/mcp.json`, для одного проекта —
`<репозиторий>/.cursor/mcp.json`. Сервер локальный, транспорт stdio: клиент сам запускает команду
и общается с ней через stdin/stdout.

### С бинарником

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "/absolute/path/to/mcp-testops-darwin-arm64",
      "args": [],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "****",
        "TESTOPS_PROJECT_ID": "65",
        "TESTOPS_READ_ONLY": "true"
      }
    }
  }
}
```

### С пакетом Python

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "mcp_testops"],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "****",
        "TESTOPS_PROJECT_ID": "65"
      }
    }
  }
}
```

- **Путь к команде — абсолютный.** Клиент запускает сервер из неожиданного рабочего каталога, относительный
  путь или голое имя из виртуального окружения не найдётся.
- **Токен — только в локальном файле.** Если `mcp.json` лежит в репозитории, пишите `"${env:TESTOPS_TOKEN}"`:
  Cursor подставит переменную окружения, и секрет в git не попадёт. В этом README вместо него `****`.
- **Окружение сервера — это ровно этот блок `env`.** Переменные вашей оболочки в процесс сервера
  не попадают, поэтому `TESTOPS_BASE_URL` и `TESTOPS_PROJECT_ID` лучше указать явно.
- **Проверка:** после сохранения файла перезагрузите конфиг MCP (Cursor: Customize → MCPs) и убедитесь,
  что в списке 30 инструментов — тогда сервер ответил на `initialize`.

Остальные клиенты, которые запускают локальную команду по stdio (Claude Desktop,
`~/.config/...`-подобные), используют ту же пару `command`/`args` плюс свой `env`; в Claude Desktop это
`claude_desktop_config.json` с тем же объектом `mcpServers`.

### Запуск без установки

Если не хочется держать файл и путь к нему, клиенту можно отдать команду, которая всё делает сама:

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gribanoveu/mcp-testops"],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "****"
      }
    }
  }
}
```

Первый запуск скачивает бинарник вашей платформы (~22–40 МБ) в `~/.cache/mcp-testops/`, следующие идут
из кеша. Если пакет поставлен глобально (`npm i -g @gribanoveu/mcp-testops`), то в конфиге хватит
`"command": "mcp-testops"` без `args`. Без Node есть вариант с `uv`: `"command": "uvx"`,
`"args": ["--from", "git+https://github.com/gribanoveu/mcp-testops", "mcp-testops"]`, а когда пакет
будет на PyPI — просто `"args": ["mcp-testops"]`.

## Ограничения и риски

- **Авторизация не подтверждена спекой:** в снимке нет `security`/`securitySchemes`; используется
  `Authorization: Api-Token <token>` — это допущение (`docs/06-open-questions.md`, вопрос 1). При 401/403
  первым делом проверить, не нужен ли `Bearer`.
- **`TESTOPS_VERIFY_SSL=false` по умолчанию** — осознанное послабление для самоподписанного CA: TLS не
  проверяется. На стенде с валидным сертификатом выставлять `true`.
- **`TESTOPS_READ_ONLY`** скрывает 13 write-инструментов из 30; на рабочем проекте включать явно.
- **Нет generic-вызова и загрузки файлов:** дерево, общие шаги, дефекты, вложения и импорт результатов
  через MCP недоступны; для вложений и архивов нужен отдельный именованный инструмент (multipart
  JSON-строкой не собрать).
- **Удаление кейса — мягкое:** `DELETE /api/testcase/{id}` отвечает `202` и уводит кейс в корзину;
  восстановление не выведено (`docs/06-open-questions.md`, вопрос 8).
- **Логи:** только метод, путь, код и длительность; токен, заголовки и тела не пишутся. Логгер `httpx`
  при старте приглушён — он логирует полные URL вместе с текстом `rql`.

## Разработка и проверка

```bash
python -m py_compile src/mcp_testops/*.py src/mcp_testops/tools/*.py
pytest -q                                        # 56 тестов; 12 контрактных — со снимком спеки
mcp version                                      # версия официального SDK
mcp dev src/mcp_testops/__init__.py              # Inspector: что увидит модель
python -m mcp_testops                            # stdio, читает TESTOPS_* из env
```

Собрать standalone-бинарник локально (то же, что делает релизный workflow):

```bash
pip install -e ".[build]"
pyinstaller --onefile --name mcp-testops --distpath dist-bin --workpath build/pyi \
  --collect-submodules mcp.server --collect-all pydantic --collect-all anyio \
  --hidden-import mcp_testops packaging/entry.py
```

Переснять снимок спеки перед этапом и посмотреть дифф:

```bash
scripts/refresh_spec.sh          # curl /api-docs/ в openapi/api-docs.json.new + дифф путей и схем
```

Скрипт не перезаписывает `openapi/api-docs.json`: сначала читаются версия и дифф, потом снимок меняется
и гоняются `pytest -q`. Полного снимка в репозитории нет — его получают этим скриптом со своего стенда;
пока снимка нет, `tests/test_contract.py` помечается skipped, остальные 56 тестов работают.

## Скилл для агента

В `skills/testops-mcp/SKILL.md` — инструкция для модели: карта из 30 инструментов, готовые цепочки
(найти кейс → шаги → прогон → результаты), формы JSON-аргументов, чего инструменты не умеют и что
делать, если ответ не тот. Положите каталог `skills/testops-mcp/` в папку скиллов клиента (Kibo,
Claude Code) — он подхватит его по описанию из frontmatter.

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
├── scripts/refresh_spec.sh  # получить снимок спеки с вашего стенда
├── openapi/              # выборки из спеки: api-inventory.md, key-schemas.json
├── docs/                 # аналитика API и план, по которым писался сервер (01–06)
├── packaging/entry.py     # точка входа для standalone-бинарника
├── npm/                  # обёртка `npx -y @gribanoveu/mcp-testops`
├── skills/testops-mcp/    # SKILL.md — как пользоваться сервером агенту
├── AGENTS.md             # правила работы над сервером
├── CHANGELOG.md          # что сделано, по этапам
├── LICENSE               # MIT
└── pyproject.toml        # hatchling, mcp>=2,<3, httpx
```

## Документация

`docs/` — аналитика, а не описание готового сервера:

| Документ | О чём |
|---|---|
| `docs/01-contract.md` | устройство API: авторизация, пагинация, ошибки, AQL, полиморфные ответы |
| `docs/02-domain-model.md` | сущности и связи: Project → TestCase → TestPlan → Launch → TestResult |
| `docs/03-tools-spec.md` | спецификация инструментов: сигнатура, эндпоинт, тело, ответ |
| `docs/04-current-implementation.md` | разбор чужого примера и его ошибок (Д1–Д11) — «чего не делать»; сам снимок примера из репозитория убран |
| `docs/05-plan.md` | этапы M0–M4 и критерии приёмки |
| `docs/06-open-questions.md` | что проверить на стенде: авторизация, синтаксис AQL, лимиты, дерево |

Если документ расходится с кодом, прав код: источник правды — `openapi/api-docs.json` и контрактные
тесты. Что сделано на каждом этапе — `CHANGELOG.md`.
