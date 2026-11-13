# mcp-testops — MCP-сервер для Allure TestOps

MCP-сервер (stdio) поверх API Allure TestOps: проекты, тест-кейсы с шагами, тест-планы, запуски и
результаты, справочники. **30 инструментов: 17 читают, 13 меняют**; generic-вызова «любой путь под
`/api`» нет сознательно (`docs/03-tools-spec.md` §7). Python 3.10+, официальный SDK `mcp` v2
(`MCPServer` из `mcp.server`) и `httpx`; сервер не слушает портов — клиент запускает его подпроцессом.
Лицензия MIT.

## Установка

```bash
npx -y @gribanoveu/mcp-testops                                         # Node 18+, без установки
npm install -g @gribanoveu/mcp-testops                                 # глобально: команда mcp-testops
uvx --from git+https://github.com/gribanoveu/mcp-testops mcp-testops   # через uv, Python 3.10+
pip install https://github.com/gribanoveu/mcp-testops/releases/download/v0.1.9/mcp_testops-0.1.9-py3-none-any.whl
```

Обёртка `npx` Python не требует: при первом запуске она скачивает бинарник своей платформы (22–40 МБ)
из [Releases](https://github.com/gribanoveu/mcp-testops/releases) в `~/.cache/mcp-testops/` и дальше
работает из него. Готовые бинарники лежат там же: darwin-arm64, linux-x64, linux-arm64, win32-x64.

Версия закрепляется на любой форме: `npx -y @gribanoveu/mcp-testops@0.1.9`. Чем эти пути различаются,
что делать на Intel Mac и какие клиенты поддерживаются — [docs/07-clients.md](docs/07-clients.md).

## Настройка

Всё, что зависит от стенда, приходит из окружения: один пакет поднимается под разные проекты.

| Переменная | Обязательна | По умолчанию | Смысл |
|---|---|---|---|
| `TESTOPS_TOKEN` | да | — | API-токен; без него старт прерывается с `TESTOPS_TOKEN is not set` |
| `TESTOPS_BASE_URL` | нет | `https://testops.net` | хост стенда |
| `TESTOPS_PROJECT_ID` | нет | — | проект по умолчанию для инструментов без `project_id` |
| `TESTOPS_VERIFY_SSL` | нет | `false` | проверка TLS; `true` на стенде с валидным сертификатом |
| `TESTOPS_TIMEOUT` | нет | `60` | таймаут запроса, секунды |
| `TESTOPS_READ_ONLY` | нет | `false` | `true` — регистрируются только read-инструменты (17 из 30) |
| `MCP_SERVER_NAME` | нет | `testops` | имя сервера в клиенте |

Флаги принимают `1`, `true`, `yes`, `on` в любом регистре. Токен уходит как
`Authorization: Api-Token <token>`; при `401`/`403` попробуйте `Bearer`. Остальное — прокси, CA,
ретраи, логи, почему TLS по умолчанию выключен — [docs/08-limitations.md](docs/08-limitations.md).

## Подключение

Один JSON-объект `mcpServers` с `command`/`args`/`env` понимают почти все клиенты: Cursor
(`~/.cursor/mcp.json` или `.cursor/mcp.json`), Claude Desktop (`claude_desktop_config.json`),
Claude Code (`.mcp.json`), Gemini CLI (`settings.json`), Kiro (`.kiro/settings/mcp.json`), Kibo Agent
(`~/.kibo/mcp.json`), Trae, Devin CLI, Factory Droid. Содержимое у всех одно:

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gribanoveu/mcp-testops"],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "****",
        "TESTOPS_PROJECT_ID": "65"
      }
    }
  }
}
```

- токен в репозитории не храните: пишите `"${env:TESTOPS_TOKEN}"` — клиент подставит переменную
  окружения, а в git секрет не попадёт;
- сервер видит **только** этот блок `env` — переменные вашей оболочки до него не доходят;
- клиенты без строки `type` (Claude Desktop, Kiro) её просто игнорируют; `TESTOPS_READ_ONLY` — `true`,
  если нужен доступ без записи.

### Claude Code

```bash
claude mcp add testops -e TESTOPS_TOKEN=... -e TESTOPS_BASE_URL=https://testops.net \
  -- npx -y @gribanoveu/mcp-testops
```

`-s user` — для всех проектов (`~/.claude.json`), `-s project` — в `.mcp.json` проекта; проверить —
`claude mcp list`.

### VS Code (GitHub Copilot)

Ключ другой — `servers` вместо `mcpServers`, и `type` обязателен. Файл `.vscode/mcp.json` (или
пользовательский профиль); секреты можно вынести в `inputs`:

```json
{
  "servers": {
    "testops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gribanoveu/mcp-testops"],
      "env": { "TESTOPS_BASE_URL": "https://testops.net", "TESTOPS_TOKEN": "${input:testops-token}" }
    }
  },
  "inputs": [{ "id": "testops-token", "type": "promptString", "description": "TestOps API token", "password": true }]
}
```

### Остальные форматы

- **Zed** — `.zed/settings.json`, ключ `context_servers` (внутри `command: {path, args, env}`).
- **Codex CLI** — TOML в `~/.codex/config.toml`, таблица `[mcp_servers.testops]` с `command`, `args`,
  `env`.
- **OpenCode** — `opencode.json`, ключ `mcp` с `type: "local"` и массивом `command`.
- **Транспорты** бывают два: stdio (`command`/`args`, как здесь) и Streamable HTTP (`url`/`headers`,
  SSE — устаревший). Этот сервер работает только по stdio: портов не слушает и никуда не ходит, кроме
  стенда `TESTOPS_BASE_URL`.

Варианты с абсолютным путём к бинарнику и с Python-пакетом, а также полный список клиентов —
[docs/07-clients.md](docs/07-clients.md).

## Скилл для агента

Рядом с сервером лежит скилл для модели: карта из 30 инструментов, готовые цепочки, формы аргументов и
референс AQL (`aql.md` — поля, операторы, даты, подполя). Английский, как и docstring инструментов.

```bash
npx -y skills add gribanoveu/mcp-testops --skill testops-mcp   # Skills CLI, в проект; -g — глобально
npx -y @gribanoveu/mcp-testops skill -g                         # из npm-пакета, в ~/.agents/skills
```

Скилл едет внутри npm-пакета и лежит в [каталоге Kibo](https://github.com/gribanoveu/kibo-agent-catalog)
рядом с записью MCP-сервера.

## Разработка

```bash
pip install -e ".[test]"
pytest -q          # 63 теста: 62 passed, 1 skipped — контрактный, пока нет снимка спеки
```

Сборка бинарников, `scripts/refresh_spec.sh` и публикация (trusted publishing по OIDC, staged-версии
в npm) — [docs/09-development.md](docs/09-development.md).
