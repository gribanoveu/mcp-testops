# Установка и подключение

Сервер локальный, транспорт stdio: клиент сам запускает команду и общается с ней через stdin/stdout.
Поэтому в конфиге клиента важны ровно три вещи — `command`, `args` и `env`.

## Чем ставить

| Способ | Что нужно | Команда |
|---|---|---|
| npm | Node 18+ | `npx -y @gribanoveu/mcp-testops` |
| npm, глобально | Node 18+ | `npm install -g @gribanoveu/mcp-testops`, затем `mcp-testops` |
| uv | Python 3.10+ и `uv` | `uvx --from git+https://github.com/gribanoveu/mcp-testops mcp-testops` |
| колесо | Python 3.10+ | `pip install <url колеса из Releases>`, затем `python -m mcp_testops` |
| бинарник | ничего | скачать ассет из Releases, `chmod +x`, запускать по абсолютному пути |

Обёртка npm ставит не сервер, а загрузчик: при первом запуске она берёт бинарник своей платформы
(22–40 МБ) из этого же Release в `~/.cache/mcp-testops/<version>/` и дальше запускает его. Всё
служебное пишется в stderr — stdout остаётся протоколу MCP.

**Ассеты релиза:** `mcp-testops-darwin-arm64`, `mcp-testops-linux-x64`, `mcp-testops-linux-arm64`,
`mcp-testops-win32-x64.exe`.

**Intel Mac:** готового бинарника нет — сборка под x64 на раннере GitHub падает на несовпадении OpenSSL
в `cryptography`. Там ставьте колесо или `uvx`. Обёртка `npx` на Intel Mac честно скажет об этом, а не
упадёт на 404.

**Версии:** закрепить можно на любой форме — `npx -y @gribanoveu/mcp-testops@0.1.9`,
`pip install .../v0.1.9/mcp_testops-0.1.9-py3-none-any.whl`. Обновление — тем же способом.

**PyPI пока нет:** `uvx mcp-testops` без `--from` не работает, пока у проекта не появится trusted
publisher. Состояние публикации описано в `docs/08-limitations.md`.

## Cursor

`~/.cursor/mcp.json` — для всех проектов, `<репозиторий>/.cursor/mcp.json` — для одного.

### Без установки (npm)

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gribanoveu/mcp-testops"],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "${env:TESTOPS_TOKEN}",
        "TESTOPS_PROJECT_ID": "65"
      }
    }
  }
}
```

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
        "TESTOPS_TOKEN": "${env:TESTOPS_TOKEN}",
        "TESTOPS_PROJECT_ID": "65",
        "TESTOPS_READ_ONLY": "true"
      }
    }
  }
}
```

### С Python-пакетом

```json
{
  "mcpServers": {
    "testops": {
      "type": "stdio",
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "mcp_testops"],
      "env": {
        "TESTOPS_BASE_URL": "https://testops.net",
        "TESTOPS_TOKEN": "${env:TESTOPS_TOKEN}",
        "TESTOPS_PROJECT_ID": "65"
      }
    }
  }
}
```

## Что важно, независимо от клиента

- **Путь к команде — абсолютный.** Клиент запускает сервер из неожиданного рабочего каталога, поэтому
  относительный путь или голое имя из виртуального окружения не найдутся. Для `npx`/`uvx` это не
  проблема — они в PATH.
- **Токен — только в локальном файле.** В репозитории пишите `"${env:TESTOPS_TOKEN}"`: Cursor подставит
  переменную окружения, и секрет не попадёт в git. В примерах выше так и сделано.
- **Окружение сервера — это ровно блок `env`.** Переменные вашей оболочки в процесс не попадают, поэтому
  `TESTOPS_BASE_URL` и `TESTOPS_PROJECT_ID` указывайте явно.
- **Проверка:** перезагрузите конфиг MCP (Cursor: Customize → MCPs). В списке должно быть 30 инструментов
  (17 при `TESTOPS_READ_ONLY=true`) — значит сервер ответил на `initialize`.

## Другие клиенты

Любой клиент, который умеет запускать локальную команду по stdio, использует ту же пару
`command`/`args` плюс свой `env`:

- **Claude Desktop** — `claude_desktop_config.json` с тем же объектом `mcpServers` (без
  `"type": "stdio"`);
- **Claude Code** — `claude mcp add testops -e TESTOPS_TOKEN=... -e TESTOPS_BASE_URL=https://testops.net
  -- npx -y @gribanoveu/mcp-testops`, ключ `-s user` для всех проектов или `-s project` в `.mcp.json`;
- **Kibo Agent** — страница Catalog: записи «Allure TestOps» (MCP-сервер и скилл) из
  [kibo-agent-catalog](https://github.com/gribanoveu/kibo-agent-catalog); значения `TESTOPS_*` он
  спросит при установке и запишет в `~/.kibo/mcp.json`.

## Скилл

```bash
npx -y skills add gribanoveu/mcp-testops --skill testops-mcp      # Skills CLI: в проект
npx -y skills add gribanoveu/mcp-testops --skill testops-mcp -g   # глобально, ~/.agents/skills
npx -y @gribanoveu/mcp-testops skill -g                           # из npm-пакета, туда же
npx -y @gribanoveu/mcp-testops skill --dir .cursor/skills         # или в явную папку
```

Ставится каталог целиком — `SKILL.md` и `aql.md`. Руками — скопировать `skills/testops-mcp/` в папку
скиллов клиента.
