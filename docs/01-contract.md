# 01. Контракт API

Источник — снимок `../openapi/api-docs.json` (`allure-testops-service` 527u04). Все утверждения ниже
проверены по нему; то, что проверить по спецификации нельзя, помечено «допущение».

## 1. Формат и объём

| Параметр | Значение |
|---|---|
| OpenAPI | 3.1.0 |
| Сервер | `servers: [{"url": "/"}]` — все пути относительны, база = `https://<host>` |
| База API | все пути начинаются с `/api` (`/api/testcase`, `/api/v2/...`) |
| Путей | 634 |
| Операций | 845: GET 357, POST 331, DELETE 78, PATCH 71, PUT 8 |
| Тегов | 176 (это контроллеры, а не домены) |
| Схем | 803, все в `components.schemas`; `components.securitySchemes`, `components.responses`, `components.parameters` отсутствуют |
| Deprecated | 11 операций, из них для нас важны `/api/cf`, `/api/cfv`, `GET /api/testcase/{id}/scenario` |

Распределение по префиксам (полный список — `../openapi/api-inventory.md`):

| Префикс | Операций |
|---|---|
| `/api/testcase` | 101 |
| `/api/testresult` | 58 |
| `/api/integration` | 55 |
| `/api/launch` | 55 |
| `/api/v2` | 46 |
| `/api/project` | 37 |
| `/api/sharedstep` | 22 |
| `/api/defect` | 19 |
| `/api/testplan` | 17 |

## 2. Авторизация

- В спецификации **нет** ни `security` на операциях, ни `securitySchemes` в компонентах — контракт
  авторизацию не описывает.
- **Допущение:** используется `Authorization: Api-Token <token>` — так реализовано в текущей заготовке
  (`/api/token` существует в API: `GET`, `POST`, `DELETE /api/token/{id}`). Подтвердить на стенде
  (`06-open-questions.md`, вопрос 1).
- Токен — только через env, никогда в коде/README/логах. Заголовки запросов не логировать.

## 3. Конфигурация

| Переменная | Обязательна | Значение по умолчанию | Смысл |
|---|---|---|---|
| `TESTOPS_BASE_URL` | нет | `https://testops.moscow.alfaintra.net` | хост стенда |
| `TESTOPS_TOKEN` | да | — | API-токен |
| `TESTOPS_PROJECT_ID` | нет | — | проект по умолчанию, если инструмент вызван без `project_id` |
| `TESTOPS_VERIFY_SSL` | нет | `false` | проверка TLS; внутренний стенд на самоподписанном CA |
| `TESTOPS_TIMEOUT` | нет | `60` | таймаут запроса, секунды |
| `TESTOPS_READ_ONLY` | нет | `false` | `true` — только read-инструменты |
| `MCP_SERVER_NAME` | нет | `testops` | имя сервера в opencode |

`TESTOPS_VERIFY_SSL=false` — осознанное послабление: без него внутренний стенд не отвечает.
В README это должно быть названо риском, а не спрятано в дефолте.

## 4. Пагинация (Spring Data)

Параметр `page` встречается в 170 операциях — это единый механизм для всех листингов.

| Параметр | Тип | По умолчанию | Примечание |
|---|---|---|---|
| `page` | int ≥ 0 | `0` | номер страницы |
| `size` | int ≥ 1 | `10` | размер страницы |
| `sort` | string[] | зависит от ресурса | формат `property,ASC\|DESC`, можно несколько |

Проверенные значения `sort` по умолчанию:

| Эндпоинт | `sort` |
|---|---|
| `GET /api/testcase` | `["createdDate,DESC"]` |
| `GET /api/testcase/__search` | `["id,DESC"]` |
| `GET /api/testresult` | `["createdDate,DESC"]` |
| `GET /api/launch` | `["created_date,DESC"]` (именно с подчёркиванием) |
| `GET /api/testplan` | `["name,ASC"]` |
| `GET /api/project` | `["name,ASC"]` |
| `GET /api/testlayer`, `GET /api/cf` | `["id,ASC"]` |

Ответ — конверт `Page*Dto`:

```json
{
  "content": [ ... ],
  "totalElements": 0, "totalPages": 0, "number": 0, "size": 10,
  "numberOfElements": 0, "first": true, "last": true, "empty": true,
  "pageable": { "pageNumber": 0, "pageSize": 10, "offset": 0, "paged": true, "unpaged": false,
                "sort": { "sorted": true, "unsorted": false, "empty": false } },
  "sort": { "sorted": true, "unsorted": false, "empty": false }
}
```

Практика для инструмента: по умолчанию просить `size=50` (а не 10), но **не больше 100** за запрос,
и возвращать наружу `content` + `totalElements`/`totalPages`/`number`, чтобы модель понимала, что
список обрезан.

## 5. Коды и ошибки

| Код | Когда | Что означает для клиента |
|---|---|---|
| `200` | обычный ответ | JSON в теле |
| `202` | bulk-операции, удаление кейса, загрузка | принято асинхронно, тела нет; результат — позже |
| `204` | `DELETE /api/launch/{id}` | успех без тела |
| `4xx` | ошибка запроса | тело — JSON с полем `message` (так разбирает текущий клиент) |
| `5xx` | ошибка сервера | ретрай с backoff (кроме POST, создающих сущности) |

Ответы объявлены с медиатипом `*/*` — то есть `Accept` можно не задавать, сервер отвечает JSON.

## 6. Полиморфные ответы

`GET /api/launch` объявляет `oneOf: [PageLaunchPreviewDto, PageLaunchDto]` — это не ошибка схемы, а
разные представления в зависимости от параметров/настроек проекта. Клиент обязан разбирать оба:

- `LaunchPreviewDto` — `statistic`, `environment`, `jobs`, `newDefectsCount`, `knownDefectsCount`;
- `LaunchDto` — `closed`, `autoclose`, `release`, `tags`, плюс общие `id`, `name`, `projectId`,
  `createdDate`, `links`, `issues`.

Аналогично сценарии: `TestCaseScenarioV2Dto.steps` — массив `oneOf`
(`AttachmentStepDto` | `BodyStepDto` | `ExpectedBodyStepDto` | `SharedStepStepDto`), различитель —
поле `type` (`ScenarioStepDto.discriminator.propertyName = "type"`).

## 7. AQL (в API — `rql`)

| Что | Эндпоинт |
|---|---|
| Поиск кейсов | `GET /api/testcase/__search?projectId&rql&deleted&page&size&sort` → `PageTestCaseDto` |
| Проверка запроса кейсов | `GET /api/testcase/query/validate?projectId&rql&deleted` → `{valid, count}` |
| Поиск запусков | `GET /api/launch/__search` (аналогично) |
| Проверка запроса запусков | `GET /api/launch/query/validate` |
| Сохранённые фильтры | `/api/filter`, `/api/filter/base`, `/api/filter/{id}` |

Параметры `tcRql` (6 операций) и `launchRql` (4) — то же самое, но внутри тест-планов и джобов.

`__search` возвращает **полные** `TestCaseDto` (в отличие от листинга, который отдаёт строки), поэтому
из него сразу видны `tags`, `links`, `status`, `workflow`, `testLayer`.

## 8. Обязательность `projectId`

| Эндпоинт | Обязательные параметры |
|---|---|
| `GET /api/testcase` | `projectId` |
| `GET /api/testcase/__search` | `projectId`, `rql` |
| `GET /api/testplan` | `projectId` |
| `GET /api/launch` | `projectId` |
| `GET /api/testresult` | `launchId` |
| `POST /api/testcase` | в теле `name`, `projectId` |
| `POST /api/launch` | в теле `name`, `projectId` |
| `POST /api/testplan` | в теле `name`, `projectId` |
| `POST /api/testresult` | в теле `launchId`, `name`, `status` |
| `POST /api/testcase/bulk/run/new` | в теле `launchName`, `selection` (а в `selection` — `projectId`) |

Отсюда правило: `TESTOPS_PROJECT_ID` подставляется, только если аргумент не передан, и в ответе
должно быть видно, какой проект использован (иначе агент молча пишет в чужой проект).

## 9. Загрузка файлов и асинхронность

- `POST /api/launch/{launchId}/upload`, `/upload/archive`, `/upload/file` — загрузка результатов прогона;
- `POST /api/upload?id=<launchId>` — `multipart/form-data` с `file[]`/`archive[]`, ответ `202`;
- `POST /api/upload/session`, `/start`, `/stop`, `/run` — сессионная загрузка (для агентов прогонов);
- вложения кейсов/результатов/общих шагов: `POST /api/testcase/attachment`,
  `POST /api/testresult/attachment`, `POST /api/sharedstep/attachment`, содержимое —
  `GET|PUT /api/<area>/attachment/{id}/content`.

`202` означает «принято»: в схеме есть `AsyncJobDto` (`id`, `name`, `status`) со
`AsyncJobStatusDto = IN_PROGRESS | FAILED | COMPLETED | STOPPED | CANCELLED`. **Путь опроса задания в
спецификации я не нашёл** — открытый вопрос 3.

## 10. Заголовки

Спецификация не объявляет ни одного header-параметра (проверено: множество header-параметров пусто).
Значит, `Accept`, `Content-Type` и авторизация — единственные заголовки, которые имеет смысл ставить;
никакие `X-Project-Id` или версии API через заголовки не передаются.
