# Changelog

Что сделано, по этапам из `docs/05-plan.md`: одна строка на этап, новое — сверху.

## 2026-11-09 — M0. Каркас пакета

- Поднят каркас `mcp-testops` на официальном SDK `mcp` v2 (`MCPServer` из `mcp.server`, проверено
  на 2.3.0): `pyproject.toml` (hatchling, `mcp>=2,<3`, `httpx>=0.27`, тестовые `pytest`/`jsonschema`),
  `src/mcp_testops/`. Без `TESTOPS_TOKEN` запуск падает с `TESTOPS_TOKEN is not set`, с токеном сервер
  отвечает на `initialize` по stdio.
- Аналитика переехала в `docs/` (01–06), перекрёстные ссылки поправлены; правила для агентов остаются
  в `AGENTS.md` в корне.
