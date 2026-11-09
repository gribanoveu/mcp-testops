# Фрагменты `MMBMB/mcp-testops` (HEAD `ad9c4daa`, снято 2026-11-09)

Цитаты из `src/mcp_testops/__init__.py` с номерами строк оригинала. Пробелы и формулировки docstring —
как в источнике. Фрагменты выбраны под дефекты из `../docs/04-current-implementation.md`.

---

## Конфигурация и импорт SDK — строки 1–40

```python
"""MCP server for Allure TestOps (testops.moscow.alfaintra.net).

Thin REST client over the allure-testops-service API (version 526u04).
Configuration is provided through environment variables so one codebase can be
instantiated for many projects, mirroring the existing mcp-oracle servers:

    MCP_SERVER_NAME      - server name shown in opencode (optional)
    TESTOPS_BASE_URL     - e.g. https://testops.moscow.alfaintra.net
    TESTOPS_TOKEN        - API token (Authorization: Api-Token <token>)
    TESTOPS_PROJECT_ID   - default project id used when not passed to a tool

Run via stdio:
    python -m mcp_testops
"""
```

```python
try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover
    sys.stderr.write("ERROR: install dependencies first: pip install -e .\n")
    sys.exit(1)


SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "testops")
BASE_URL = os.environ.get("TESTOPS_BASE_URL", "https://testops.moscow.alfaintra.net").rstrip("/")
TOKEN = os.environ.get("TESTOPS_TOKEN", "")
DEFAULT_PROJECT_ID = os.environ.get("TESTOPS_PROJECT_ID", "")
# Internal instances typically use a self-signed certificate; verify is off by
# default and can be re-enabled with TESTOPS_VERIFY_SSL=true.
VERIFY_SSL = os.environ.get("TESTOPS_VERIFY_SSL", "false").lower() in ("true", "1", "yes")

mcp = FastMCP(SERVER_NAME)
```

Строка 3 говорит `526u04`; стенд отдаёт `527u04` (дефект Д7).

---

## HTTP-хелперы — строки 43–107

```python
def _auth_headers() -> dict[str, str]:
    return {"Authorization": f"Api-Token {TOKEN}"}


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=BASE_URL,
        headers=_auth_headers(),
        timeout=60.0,
        verify=VERIFY_SSL,
    )


def _pid(project_id: int | None) -> int:
    if project_id is not None:
        return project_id
    if DEFAULT_PROJECT_ID:
        return int(DEFAULT_PROJECT_ID)
    raise ValueError("project_id is required (or set TESTOPS_PROJECT_ID)")


def _dump(data: Any) -> str:
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def _ok(data: Any) -> str:
    return _dump(data)


def _api(method: str, path: str, params: dict | None = None, body: Any = None) -> Any:
    """Perform an API request and return parsed JSON. Raises on non-2xx."""
    if not TOKEN:
        raise ValueError("TESTOPS_TOKEN is not set")
    with _client() as c:
        r = c.request(method, path, params=params, json=body)
    if r.status_code >= 400:
        detail = ""
        try:
            detail = r.json().get("message") or r.text
        except Exception:
            detail = r.text[:500]
        raise RuntimeError(f"HTTP {r.status_code} on {method} {path}: {detail}")
    if not r.content:
        return None
    try:
        return r.json()
    except Exception:
        return r.text


def _json_arg(value: str | None, default: Any = None) -> Any:
    if value is None or value == "":
        return default
    try:
        return json.loads(value)
    except Exception:
        return value


def _compact(payload: dict[str, Any], keys: list[str]) -> None:
    for k in list(payload):
        if payload[k] is None and k not in keys:
            payload.pop(k)
```

Дефекты: клиент на каждый вызов (Д5), `r.text` при не-JSON (Д9), `indent=2` (Д10), `_compact`
не убирает пустые строки (Д8).

---

## Пример read-инструмента — строки 115–124

```python
@mcp.tool()
def list_projects(search: str | None = None, page: int = 0, size: int = 50) -> str:
    """List TestOps projects. Optionally narrow by a text `search` term."""
    params: dict[str, Any] = {"page": page, "size": size}
    if search:
        params["search"] = search
    try:
        return _ok(_api("GET", "/api/project", params=params))
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})
```

Это удачная форма: docstring — контракт, ошибка — данные. Её и повторяем.

---

## Поиск кейсов с клиентской фильтрацией — строки 159–201 (дефект Д2)

```python
@mcp.tool()
def search_test_cases(
    project_id: int | None = None,
    name: str | None = None,
    rql: str | None = None,
    deleted: bool = False,
    page: int = 0,
    size: int = 100,
) -> str:
    """Search test cases.

    Pass a raw `rql` (AQL) query for server-side filtering, e.g.
    'name ~ "auth"' , or pass `name` for a simple case-insensitive substring
    match performed client side over the paged listing.
    """
    try:
        pid = _pid(project_id)
        if rql:
            params = {
                "projectId": pid,
                "rql": rql,
                "deleted": str(deleted).lower(),
                "page": page,
                "size": size,
            }
            return _ok(_api("GET", "/api/testcase/__search", params=params))
        wanted = (name or "").lower()
        collected: list[dict] = []
        p = 0
        while True:
            params = {"projectId": pid, "page": p, "size": min(size, 100)}
            data = _api("GET", "/api/testcase", params=params)
            items = data.get("content", [])
            for it in items:
                if not wanted or wanted in (it.get("name") or "").lower():
                    collected.append(it)
            total = data.get("totalElements", 0)
            if not items or p * (data.get("size", 1)) + len(items) >= total:
                break
            p += 1
        return _ok({"content": collected, "totalElements": len(collected), "matched": len(collected)})
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})
```

Ветка без `rql` выгружает весь проект постранично и фильтрует на клиенте.

---

## Создание кейса — строки 275–313

```python
@mcp.tool()
def create_test_case(
    project_id: int | None,
    name: str,
    description: str | None = None,
    precondition: str | None = None,
    postcondition: str | None = None,
    expected_result: str | None = None,
    status_id: int | None = None,
    workflow_id: int | None = None,
    tags_json: str | None = None,
    links_json: str | None = None,
    scenario_json: str | None = None,
) -> str:
    """Create a new manual test case. `name` and `project_id` are required.

    Optional complex fields accept JSON strings:
      tags_json      - e.g. [{"name": "smoke"}]
      links_json     - e.g. [{"name": "JIRA", "url": "https://...", "type": "issue"}]
      scenario_json  - scenario/step structure (advanced).
    """
    try:
        body: dict[str, Any] = {
            "projectId": _pid(project_id),
            "name": name,
            "description": description,
            "precondition": precondition,
            "postcondition": postcondition,
            "expectedResult": expected_result,
            "statusId": status_id,
            "workflowId": workflow_id,
            "tags": _json_arg(tags_json, None),
            "links": _json_arg(links_json, None),
            "scenario": _json_arg(scenario_json, None),
        }
        _compact(body, ["name", "projectId"])
        return _ok(_api("POST", "/api/testcase", body=body))
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})
```

Замечание: пример `tags_json` без `id` противоречит схеме `TestTagDto`, где `id` обязателен.

---

## Прогон кейсов — строки 464–494 (дефект Д1)

```python
@mcp.tool()
def run_test_cases(
    launch_name: str,
    project_id: int | None = None,
    selection_json: str | None = None,
    test_case_ids: str | None = None,
    assignees_json: str | None = None,
) -> str:
    """Run selected test cases in a new launch (creates the launch and its
    manual results). Provide a raw `selection_json` (TestCaseTreeSelectionDto)
    or a comma separated `test_case_ids` list (tree leaf ids == test case ids).
    """
    try:
        pid = _pid(project_id)
        selection: Any
        if selection_json:
            selection = _json_arg(selection_json, None)
        else:
            ids = [int(x.strip()) for x in (test_case_ids or "").split(",") if x.strip()]
            if not ids:
                raise ValueError("provide selection_json or test_case_ids")
            # leaf id == test case id for manual test case leaves
            selection = {"projectId": pid, "leafIds": ids}
        body: dict[str, Any] = {
            "launchName": launch_name,
            "selection": selection,
            "assignees": _json_arg(assignees_json, None),
        }
        return _ok(_api("POST", "/api/testcase/bulk/run/new", body=body))
    except Exception as e:
        return _ok({"ok": False, "error": str(e)})
```

Строка с `leafIds` — источник пустых прогонов: в `TestCaseTreeSelectionDto` поля `leafIds` нет,
нужно `leafsInclude`.

---

## Свободный доступ к API — строки 502–520 (дефект Д4)

```python
@mcp.tool()
def api_request(
    method: str,
    path: str,
    params_json: str | None = None,
    body_json: str | None = None,
) -> str:
    """Low-level passthrough to any TestOps endpoint.

    `path` is relative, e.g. '/api/testplan/5'. `params_json`/`body_json` are
    optional JSON strings. Useful for endpoints without a dedicated tool.
    """
    method = (method or "GET").upper()
    if not path.startswith("/api"):
        path = "/api" + path if not path.startswith("/") else path
    try:
        params = _json_arg(params_json, None)
        body = _json_arg(body_json, None)
        return _ok(_api(method, path, params=params, body=body))
```

Дальше в файле — обработчик исключения и запуск сервера; в выдержку не попали. Проверок метода и
путей нет: `DELETE /api/project/{id}` проходит.
