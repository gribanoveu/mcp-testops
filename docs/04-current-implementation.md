# 04. Разбор примера и его дефекты

> **Что здесь описано.** Пример чужой реализации, сохранённый в `../reference/` (источник — `MMBMB/mcp-testops`,
> HEAD `ad9c4daa`, снято 2026-11-09). Тот репозиторий в нашей работе не участвует: код пишется
> в этой папке, а пример нужен только как чужой опыт. Номера строк соответствуют
> `../reference/skeleton-excerpt.md`.
>
> Все Д1–Д11 — реальные ошибки этого примера, и они типовые для любой обёртки над этим API.
> Читать как «чего не делать», а не как «список правок».

## 1. Структура примера (что было в источнике)

| Файл | Что внутри |
|---|---|
| `src/mcp_testops/__init__.py` | 451 строка: конфиг, HTTP-хелперы, 21 инструмент; написан на **v1 официального SDK** (`from mcp.server.fastmcp import FastMCP`, строка 26) |
| `src/mcp_testops/__main__.py` | вызов `main()` |
| `pyproject.toml` | метаданные, entry point; зависимости `mcp>=1.0,<2` и `httpx>=0.27` — то есть заготовка на v1 SDK |
| `README.md` | установка, env, конфиг opencode, список инструментов |
| `AGENTS.md` | правила для агентов |

## 2. Хелперы (переиспользовать, но переписать)

| Что | Строки | Замечание |
|---|---|---|
| Конфиг из env: `SERVER_NAME`, `BASE_URL`, `TOKEN`, `DEFAULT_PROJECT_ID`, `VERIFY_SSL` | 32–38 | добавить `TESTOPS_TIMEOUT`, `TESTOPS_READ_ONLY` |
| `_auth_headers()` — `Authorization: Api-Token <token>` | 43–44 | оставить |
| `_client()` — новый `httpx.Client` на каждый вызов | 47–53 | **переделать на один клиент на процесс** |
| `_pid(project_id)` — дефолт из env, иначе `ValueError` | 56–61 | оставить, текст ошибки понятный |
| `_dump`, `_ok` — `json.dumps(..., ensure_ascii=False, indent=2)` | 64–71 | `indent=2` раздувает ответы; для списков лучше компактно |
| `_api(method, path, params, body)` | 74–92 | нет ретраев, нет пагинации, `r.text` при не-JSON |
| `_json_arg(value, default)` | 95–101 | оставить (JSON-строки) |
| `_compact(payload, keep)` | 104–107 | убирает только `None`, пустые строки остаются в теле |

## 3. Инструменты (21) и их строки

| Инструмент | Строки | Эндпоинт |
|---|---|---|
| `list_projects` | 115–124 | `GET /api/project` |
| `get_project` | 127–133 | `GET /api/project/{id}` |
| `list_test_cases` | 136–147 | `GET /api/testcase` |
| `get_test_case` | 150–156 | `GET /api/testcase/{id}` |
| `search_test_cases` | 159–201 | `GET /api/testcase/__search` или клиентская фильтрация |
| `list_test_plans` | 204–218 | `GET /api/testplan` |
| `get_test_plan` | 221–227 | `GET /api/testplan/{id}` |
| `list_launches` | 230–244 | `GET /api/launch` |
| `get_launch` | 247–253 | `GET /api/launch/{id}` |
| `list_test_results` | 256–267 | `GET /api/testresult` |
| `create_test_case` | 275–313 | `POST /api/testcase` |
| `update_test_case` | 316–347 | `PATCH /api/testcase/{id}` |
| `delete_test_case` | 350–356 | `DELETE /api/testcase/{id}` |
| `create_test_plan` | 364–382 | `POST /api/testplan` |
| `update_test_plan` | 385–398 | `PATCH /api/testplan/{id}` |
| `delete_test_plan` | 401–407 | `DELETE /api/testplan/{id}` |
| `create_launch` | 415–437 | `POST /api/launch` |
| `update_launch` | 440–452 | `PATCH /api/launch/{id}` |
| `delete_launch` | 455–461 | `DELETE /api/launch/{id}` |
| `run_test_cases` | 464–494 | `POST /api/testcase/bulk/run/new` |
| `api_request` | 502–520+ | любой `/api/...` |

## 4. Дефекты

### Д1 (критично). `run_test_cases` собирает несуществующее поле — прогон создаётся пустым

Строка 486:

```python
selection = {"projectId": pid, "leafIds": ids}
```

В `TestCaseTreeSelectionDto` (спека 527u04) поля `leafIds` **нет**: есть `leafsInclude` и `leafsExclude`.
Обязательный `projectId` присутствует, поэтому запрос не падает — создаётся запуск **без кейсов**, и
вызывающий агент узнаёт об этом только по пустому прогону.

**Исправление:** `{"projectId": pid, "leafsInclude": ids}` плюс контрактный тест, который валидирует
тело по схеме `TestCaseTreeSelectionDto`.

### Д2 (критично). `search_test_cases(name=…)` листает весь проект

Строки 185–199: при отсутствии `rql` инструмент постранично выгружает **все** кейсы проекта и фильтрует
на клиенте (`wanted in it["name"]`). На проекте с десятками тысяч кейсов это десятки запросов на один
вызов агента и упирается в таймаут.

**Исправление:** `name` превращать в AQL (`name ~ "<name>"`) и идти в `__search`; клиентскую выгрузку
убрать совсем.

### Д3 (важно). `get_test_case` обещает шаги, которых в ответе нет

Docstring (строка 152): «Get a full test case by id, **including scenario/steps** when present».
`TestCaseDto` не содержит ни `scenario`, ни `steps` — шаги живут в `GET /api/testcase/{id}/step`.

**Исправление:** поправить docstring, добавить `get_test_case_steps` и флаг `steps_not_included` в ответе.

### Д4 (важно). `api_request` — неограниченный доступ, включая удаление проекта

Строки 502–520: принимает любой метод и любой путь, начинающийся с `/api` (при отсутствии префикса —
молча подставляет `/api`). То есть правило «удаление проекта не выводим» обходится вызовом
`api_request("DELETE", "/api/project/65")`.

**Исправление:** сначала — allowlist/denylist префиксов, whitelist методов, запрет
`DELETE /api/project*`, уважение `TESTOPS_READ_ONLY`; затем **инструмент убран совсем**: денилист по
принципу «разрешено всё, что не перечислено» пропустил регистрацию (`/api/register`), обход через
`%61ccount` и `..` пришлось закрывать нормализацией пути, а `POST /api/testcase/bulk/remove` проходил без
валидации тела. Причина и правило — `03-tools-spec.md` §7.

### Д5 (важно). Новый `httpx.Client` на каждый вызов

`_client()` (47–53) вызывается внутри `_api()` (78–79), то есть на каждый инструмент создаётся новое
соединение, TLS-хендшейк и пул. Плюс нет ретраев на `429`/`5xx` и нет настройки таймаута (жёстко 60 с).

**Исправление:** модульный клиент, `TESTOPS_TIMEOUT`, ретраи с backoff только для идемпотентных методов.

### Д6 (важно). Нет справочников — кейс нельзя создать «правильно»

Без `/api/status`, `/api/workflow`, `/api/project/{projectId}/cf` в `create_test_case` нельзя осмысленно
заполнить `statusId`, `workflowId`, `customFields`. Модель будет угадывать id.

**Исправление:** `list_statuses` и `list_reference` (см. `03-tools-spec.md`, раздел 6).

### Д7 (средне). Расхождение версий API в документации

`README.md:3` и docstring модуля (`__init__.py:3`) говорят `526u04`, стенд отдаёт `527u04`.
README — единственный документ, который читает новый человек; расхождение создаёт ложное чувство
«мы на актуальной спеке».

**Исправление:** указать версию из `info.version` снимка и дату снятия.

### Д8 (средне). `_compact` не убирает пустые строки

Строки 104–107 удаляют только `None`. `update_test_case(description="")` отправит пустую строку и
**затрёт** описание, хотя вызывающий, скорее всего, хотел «не менять».

**Исправление:** отдельный параметр `clear: bool` или отбрасывать пустые строки по умолчанию.

### Д9 (средне). `_api` не различает «нет тела» и «не JSON»

Строки 87–92: пустой ответ → `None`; не-JSON → `r.text` (может быть HTML-страница ошибки прокси).
Инструмент вернёт мусор как успех.

**Исправление:** `204`/`202` → `{"ok": true, "accepted": true}`; не-JSON при `2xx` → ошибка
`{"ok": false, "error": "non-JSON response"}`.

### Д10 (низко). `indent=2` во всех ответах

Списки кейсов на 50 элементов с отступами раздувают контекст модели в разы.

**Исправление:** `indent=None` для листингов, `indent=2` только для одиночных объектов.

### Д11 (низко). Дубли read-кода

`list_projects`/`list_test_cases`/`list_test_plans`/`list_launches` — четыре почти одинаковые функции
`try: params… return _ok(_api(...)) except: return _ok({"ok": False…})`.

**Исправление:** общий `_paged(path, **params)` и декоратор `_guard`, который ловит исключения и
превращает в `{"ok": false}`. Меньше кода — меньше мест, где забыть `deleted` или `sort`.

## 5. Что можно оставить как есть

- Структура «один файл на сервер» — нормальна для трёх десятков инструментов; дробить на пакет стоит только когда
  появится MCP-ресурс или несколько транспортов.
- Схема именования инструментов (`verb_entity`) и возврат ошибок данными — правильные.
- `_pid()` с дефолтом из env — правильный; сохранить и добавить `projectId` в ответы.
- Хранение конфигурации целиком в env — соответствует требованию «один код — много инстансов».
