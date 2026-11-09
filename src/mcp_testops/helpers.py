"""Shared pieces of every tool: the guard, argument parsing and compaction."""

import functools
import json
from typing import Any

import httpx

from .client import TestOpsError
from .config import DEFAULT_PROJECT_ID


def _dump(payload: Any) -> str:
    """Compact JSON: a listing of 50 items must not eat the model's context."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _guard(fn):
    """Turn exceptions into data: a raise inside a tool costs the agent a turn."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return _dump(fn(*args, **kwargs))
        except TestOpsError as exc:
            return _dump({"ok": False, "error": str(exc)})
        except httpx.HTTPError as exc:
            return _dump({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
        except Exception as exc:  # a surprise is still an answer, not a lost turn
            return _dump({"ok": False, "error": f"{type(exc).__name__}: {exc}"})

    return wrapper


def _pid(project_id: int | None) -> int:
    raw = project_id if project_id is not None else DEFAULT_PROJECT_ID
    if raw is None or raw == "":
        raise TestOpsError("project_id is required (or set TESTOPS_PROJECT_ID)")
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise TestOpsError(f"project_id must be an integer, got {raw!r}")


def _aql_text(value: str) -> str:
    """Escape a value for an AQL string literal; the syntax itself is unverified."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _json_arg(value: str | None, name: str) -> Any:
    if value is None or value == "":
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise TestOpsError(f"invalid JSON in {name}: {exc}")


def _ids(value: str | None, name: str) -> list[int]:
    text = (value or "").strip()
    if not text:
        return []
    items = _json_arg(text, name) if text.startswith("[") else text.split(",")
    if not isinstance(items, list):
        raise TestOpsError(f"{name} must be a comma separated list or a JSON array")
    try:
        return [int(str(item).strip()) for item in items if str(item).strip()]
    except ValueError:
        raise TestOpsError(f"invalid id list in {name}: {value!r}")


def _drop_none(payload: dict) -> dict:
    return {k: v for k, v in payload.items() if v is not None}


def _answer(data: dict, **fields: Any) -> dict:
    """Answer of a write tool; keeps the 202 marker so an async accept is not read as a create."""
    answer = {**fields, "ok": True}
    if data.get("accepted"):
        answer["accepted"] = True
    return answer


def _pick(data: dict, keys: tuple[str, ...]) -> dict:
    """Whitelist of fields: keeps *Html duplicates and server noise out of the answer."""
    return {k: data[k] for k in keys if data.get(k) is not None}


STATUS_KEYS = ("passed", "failed", "broken", "skipped", "unknown", "in_progress")


def _statistic(raw: Any) -> dict:
    if isinstance(raw, list):
        return {
            item.get("status"): item.get("count")
            for item in raw
            if isinstance(item, dict) and item.get("status")
        }
    if isinstance(raw, dict):
        # StatisticDto (inProgress, pending, total) keeps its own key names; filtering
        # by the status list above would drop counts silently.
        return dict(raw)
    return {}
