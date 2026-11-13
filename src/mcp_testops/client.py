"""HTTP plumbing: one client per process, retries and the Page*Dto envelope."""

import logging
import time
from typing import Any

import httpx

from .config import (
    BASE_URL,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    RETRY_ATTEMPTS,
    RETRY_BACKOFF,
    RETRY_STATUSES,
    TIMEOUT,
    TOKEN,
    VERIFY_SSL,
)


class TestOpsError(Exception):
    """Returned to the model as {"ok": false, "error": ...}, never raised past a tool."""


log = logging.getLogger("mcp_testops")


def _configure_logging() -> None:
    """Silence third-party request logs: httpx writes whole URLs, including rql text."""
    logging.getLogger("httpx").setLevel(logging.WARNING)


_client: httpx.Client | None = None


def _http() -> httpx.Client:
    """One client per process: connection pool and TLS handshake are not free."""
    global _client
    if _client is None:
        _client = httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
            verify=VERIFY_SSL,
            headers={"Authorization": f"Api-Token {TOKEN or ''}"},
        )
    return _client


def _error_text(resp: httpx.Response) -> str:
    message = ""
    try:
        data = resp.json()
    except ValueError:
        data = None
    if isinstance(data, dict):
        message = str(data.get("message") or data.get("error") or "")
    where = f"{resp.request.method} {resp.request.url.path}"
    text = f"HTTP {resp.status_code} on {where}: {message or resp.reason_phrase}"
    if resp.status_code in (401, 403):
        # The two causes look the same from here: a token scheme the stand does not accept,
        # or a token that has no access to this project (a foreign case answers 403 too).
        text += " (auth: the token goes as Api-Token; if the stand wants Bearer that is a config change; 403 also means the token has no access to this project)"
    return text


def _send(method: str, path: str, params: dict | None = None, body: Any = None) -> httpx.Response:
    """Retry only idempotent calls: a replayed POST creates a second entity."""
    attempts = RETRY_ATTEMPTS if method in ("GET", "HEAD") else 1
    for attempt in range(attempts):
        started = time.monotonic()
        try:
            resp = _http().request(method, path, params=params, json=body)
        except httpx.TransportError:
            if attempt + 1 == attempts:
                raise
        else:
            # Method, path, status and time only: no query, no headers, no body.
            log.info("%s %s -> %s in %.0f ms", method, path, resp.status_code, (time.monotonic() - started) * 1000)
            if resp.status_code not in RETRY_STATUSES or attempt + 1 == attempts:
                return resp
        time.sleep(RETRY_BACKOFF * 2**attempt)
    raise TestOpsError(f"{method} {path}: no response")


def _api(method: str, path: str, params: dict | None = None, body: Any = None) -> Any:
    query = {k: v for k, v in (params or {}).items() if v is not None}
    resp = _send(method, path, query, body)
    if resp.status_code == 204:
        return {"ok": True, "accepted": True}
    if resp.status_code == 202:
        data: Any = None
        if resp.content.strip():
            try:
                data = resp.json()
            except ValueError:
                data = None
        payload = data if isinstance(data, dict) else {}
        return {**payload, "ok": True, "accepted": True}
    if not resp.is_success:
        raise TestOpsError(_error_text(resp))
    if not resp.content.strip():
        return {"ok": True}
    try:
        return resp.json()
    except ValueError:
        raise TestOpsError(f"non-JSON response from {method} {path} (HTTP {resp.status_code})")


def _paged(
    path: str,
    params: dict | None = None,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
    sort: str = "",
) -> dict:
    """One place that knows the Page*Dto envelope, so no tool re-implements it."""
    query = {**(params or {}), "page": max(0, page), "size": max(1, min(size, MAX_PAGE_SIZE))}
    if sort:
        query["sort"] = sort
    data = _api("GET", path, params=query)
    if not isinstance(data, dict) or "content" not in data:
        raise TestOpsError(f"unexpected paged response from GET {path}")
    return {
        "content": data.get("content") or [],
        "totalElements": data.get("totalElements"),
        "totalPages": data.get("totalPages"),
        "number": data.get("number"),
        "size": data.get("size"),
    }
