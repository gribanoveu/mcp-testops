# 02. Объектная модель TestOps

Схемы — из `../openapi/key-schemas.json` (имена совпадают с именами в спецификации, так их проще искать).
`?` — поле необязательное, `!` — обязательное (в `required`).

## 1. Карта связей

```
Project (!id, !name, abbr, isPublic, isVersioned, launchCount, automationPercent)
 │
 ├─ TestCase (!name, !projectId при создании)
 │    ├─ status      → StatusDto      (справочник /api/status, привязан к workflow)
 │    ├─ workflow    → WorkflowDto    (/api/workflow, /api/workflowschema)
 │    ├─ testLayer   → TestLayerDto   (/api/testlayer)
 │    ├─ tags[]      → TestTagDto (id, name)
 │    ├─ links[]     → ExternalLinkDto (name, type, url)
 │    ├─ members[]   → MemberDto (id, name, role)
 │    ├─ customFields[] → CustomFieldValueWithCfDto
 │    └─ сценарий    → отдельный ресурс: NormalizedScenarioDto через /api/testcase/{id}/step
 │
 ├─ TestPlan (!name, !projectId, baseRql, treeId, treeSelection)
 │    └─ собирается AQL-запросом (baseRql) по дереву проекта
 │
 ├─ Launch (!name, !projectId; autoclose, closed, releaseId, tags[], links[], issues[])
 │    └─ TestResult (!launchId, !name, !status)
 │         ├─ testCaseId  — кейс, из которого создан результат (может быть null для «ручного»)
 │         ├─ status      — enum TestStatus
 │         └─ те же поля описания, что и у кейса (precondition, description, expectedResult, …)
 │
 └─ Дерево: /api/testcasetree (группы и листья), /api/tree-folder
```

Идентификаторы — целые числа (`int64`), не UUID. В дереве **id листа совпадает с id кейса** для ручных
кейсов — это утверждение из текущей реализации (`run_test_cases`, строка 485, «leaf id == test case id»),
спецификацией оно не описано; проверить (вопрос 11 в `06-open-questions.md`). Для групп — своё
пространство id.

## 2. Project

`ProjectDto`, required: `id`, `name`, `isPublic`, `isVersioned`.

| Поле | Тип | Зачем в MCP |
|---|---|---|
| `id`, `name`, `abbr` | int / string | идентификация проекта, дефолт из env |
| `isPublic`, `isVersioned` | bool | версионирование кейсов включает `/api/testcase/version*` |
| `launchCount`, `automationPercent` | int / number | сводка для агента |
| `description`, `descriptionHtml` | string | **`descriptionHtml` наружу не отдаём** |
| `favorite` | bool | листинг `?favorite=true` |

Эндпоинты: `GET /api/project` (`query[]`, `my`, `favorite`, `search`, `filterId`, пагинация),
`GET /api/project/{id}`, `POST /api/project` (`ProjectCreateDto`), `PATCH /api/project/{id}`,
`GET /api/project/{id}/stats`, `/api/project/{id}/suggest`, `/api/project/count-test-cases`.
Удаление проекта инструментом **не выводим**.

## 3. TestCase

### 3.1 Два представления, и это важно

| Эндпоинт | Схема | Что внутри |
|---|---|---|
| `GET /api/testcase?projectId` | `PageTestCaseRowDto` → `TestCaseRowDto` | `id`, `name`, `status`, `automated`, `flaky`, `testLayer` — **без описания и шагов** |
| `GET /api/testcase/__search?projectId&rql` | `PageTestCaseDto` → `TestCaseDto` | полный кейс |
| `GET /api/testcase/{id}` | `TestCaseDto` | полный кейс |

`TestCaseDto` (required: нет): `id`, `name`, `fullName`, `projectId`, `description`(+`Html`),
`precondition`(+`Html`), `postcondition`(+`Html`), `expectedResult`(+`Html`), `duration`, `status`,
`workflow`, `testLayer`, `tags[]`, `links[]`, `automated`, `external`, `deleted`, `flaky`, `editable`,
`hash`, `createdBy`, `createdDate`, `lastModifiedBy`, `lastModifiedDate`.

**`scenario`/`steps` в `TestCaseDto` отсутствуют.** Шаги — отдельный вызов:

```
GET /api/testcase/{id}/step → NormalizedScenarioDto
{
  "root": NormalizedScenarioStepDto,
  "scenarioSteps": { "<id>": NormalizedScenarioStepDto, ... },
  "attachments": { "<id>": ...AttachmentRowDto },
  "sharedStepAttachments": { ... }
}
```

`NormalizedScenarioStepDto`: `id`, `body`, `bodyJson`, `expectedResult`, `expectedResultId`,
`attachmentId`, `sharedStepId`, `children[]` (id детей), `testCaseId`, `archived`,
`createdBy/Date`, `lastModifiedBy/Date`. Дерево собирается по `children`.

`GET /api/testcase/{id}/scenario` (deprecated) → `TestCaseScenarioDto` с `TestCaseScenarioStepDto`
(`name`, `keyword`, `steps[]`, `expectedResult`, `attachments[]`) — старое представление, где у шага
есть **имя**. В актуальном (V2) имени у шага нет: текст шага живёт в `body`/`bodyJson`
(см. `06-open-questions.md`, вопрос 4).

### 3.2 Создание

`POST /api/testcase`, тело `TestCaseCreateV2Dto`, required: `name`, `projectId`.

| Поле | Тип |
|---|---|
| `name`, `fullName` | string |
| `description`, `precondition`, `postcondition`, `expectedResult` | string (markdown/HTML) |
| `statusId`, `workflowId`, `testLayerId` | int |
| `tags[]` | `TestTagDto` (`id`, `name`) — **`id` обязателен в схеме** |
| `links[]` | `ExternalLinkDto` (`name`, `type`, `url`) |
| `members[]` | `MemberDto` (`id`, `name`, `role`) |
| `customFields[]` | `CustomFieldValueWithCfDto` |
| `scenario` | `TestCaseScenarioV2Dto` (см. 3.3) |
| `automated`, `external`, `deleted` | bool |

`PATCH /api/testcase/{id}`, тело `TestCasePatchV2Dto` — все поля необязательны, дополнительно `duration`,
`flaky`. `DELETE /api/testcase/{id}?force=false` → `202`.

Прочее по кейсам: `POST /api/testcase/{id}/clone`, `POST /api/testcase/bulk/clone`, `POST /api/testcase/{id}/restore`,
`GET /api/testcase/deleted`, `GET /api/testcase/{id}/history`, `/api/testcase/{id}/stats`,
`/api/testcase/{testCaseId}/tag`, `/api/testcase/{testCaseId}/issue`, `/api/testcase/{testCaseId}/requirement`.

### 3.3 Сценарий (V2)

```json
{
  "steps": [
    { "type": "body", "body": "Открыть страницу логина" },
    { "type": "body", "body": "Ввести логин", "steps": [ { "type": "body", "body": "admin" } ] },
    { "type": "body", "body": "Нажать «Войти»", "expectedResultSteps": [ { "type": "body", "body": "Открыт дашборд" } ] }
  ]
}
```

Типы шагов (`ScenarioStepDto.discriminator = "type"`):

| Тип | Схема | Поля |
|---|---|---|
| `body` | `BodyStepDto` | `body`, `bodyJson`, `steps[]`, `expectedResultSteps[]` |
| `expected_body` (ожидаемый) | `ExpectedBodyStepDto` | `body`, `bodyJson` |
| `attachment` | `AttachmentStepDto` | `attachmentId` |
| `shared_step` | `SharedStepStepDto` | `sharedStepId` |

Добавление шага по одному: `POST /api/testcase/step`, тело `ScenarioStepCreateDto`
(`testCaseId`, `parentId`, `body`, `bodyJson`, `attachmentId`, `sharedStepId`) → `ScenarioStepCreatedResponseDto`
(`createdStepId`, `scenario`). Перезапись сценария целиком: `POST /api/testcase/{id}/scenario`
(`TestCaseScenarioV2Dto`), удаление — `DELETE /api/testcase/{id}/scenario`.

> В `key-schemas.json` значения `type` не перечислены (в спеке это свободная строка с discriminator'ом),
> поэтому имена `body`/`expected_body` — **допущение**, их надо подтвердить на стенде
> (`06-open-questions.md`, вопрос 5).

## 4. TestPlan

`TestPlanCreateDto`, required `name`, `projectId`; ещё `baseRql`, `treeId`, `treeSelection` (`TreeSelectionDto`).

`TestPlanDto`, required `baseRql`, `id`, `name`, `projectId`, `testCasesCount`; плюс `tree`, `treeSelection`,
`createdBy/Date`, `lastModifiedBy/Date`.

`TestPlanPatchDto` — `name`, `baseRql`, `treeId`, `treeSelection`.

Эндпоинты: `GET /api/testplan?projectId&search&treeId&filterId`, `GET|PATCH|DELETE /api/testplan/{id}`,
`POST /{id}/run`, `POST /{id}/assign`, `POST /{id}/sync`, `GET /{id}/stat`, `GET /{id}/diff`, `GET /{id}/job`,
`POST /{id}/jobparameter`, `POST /{id}/resetjob`, `GET /{id}/member`, `GET /{id}/tree/group`, `GET /{id}/tree/leaf`.

## 5. Launch (прогон)

`LaunchCreateDto`, required `name`, `projectId`; ещё `autoclose`, `external`, `releaseId`, `tags[]`,
`links[]`, `issues[]`.

`LaunchDto`, required `closed`, `id`, `name`, `projectId`; ещё `autoclose`, `createdBy/Date`,
`lastModifiedBy/Date`, `external`, `releaseId`, `tags[]`, `links[]`, `issues[]`.

`LaunchPreviewDto` — другое представление того же ресурса: `statistic`, `environment`, `jobs`,
`newDefectsCount`, `knownDefectsCount`, `release`, `tags`, `closed`, `id`, `name`, `projectId`.

Жизненный цикл:

| Операция | Эндпоинт |
|---|---|
| создать | `POST /api/launch` |
| изменить | `PATCH /api/launch/{id}` (`LaunchPatchDto`) |
| закрыть | `POST /api/launch/{id}/close` (без тела) |
| переоткрыть | `POST /api/launch/{id}/reopen` (без тела) |
| удалить | `DELETE /api/launch/{id}` → `204` |
| слить | `POST /api/launch/merge` |
| копировать | `POST /api/launch/{id}/copy` |
| добавить кейсы | `POST /api/launch/{id}/testcase/add` |
| добавить тест-план | `POST /api/launch/{id}/testplan/add` |
| статистика | `GET /api/launch/{id}/statistic`, `/{id}/progress`, `/{id}/duration` |
| дефекты | `GET /api/launch/{id}/defect`, `POST /{id}/defect/apply` |

## 6. TestResult

`TestResultCreateV2Dto`, required `launchId`, `name`, `status`; ещё `testCaseId`, `manual`, `external`,
`duration`, `start`, `stop`, `message`, `trace`, `description`, `precondition`, `postcondition`,
`expectedResult`, `fullName`, `tags[]`, `links[]`, `members[]`, `customFields[]`, `testLayerId`, `scenario`.

`TestStatus` = `failed | broken | passed | skipped | unknown | in_progress`.

`TestResultDto`: `id`, `name`, `fullName`, `launchId`, `projectId`, `testCaseId`, `status`, `start`, `stop`,
`duration`, `message`, `trace`, `manual`, `hidden`, `known`, `flaky`, `flakyCandidate`, `muted`, `retriedBy`,
`historyKey`, `scenarioKey`, `threadId`, `hostId`, `testedBy`, `assignee`, `category`, `layer`, `links`,
`tags`, `parameters`, `jobRun`, `description`(+`Html`), `precondition`(+`Html`), `postcondition`(+`Html`),
`expectedResult`(+`Html`), `createdBy`, `createdDate`, `lastModifiedBy`, `lastModifiedDate`.

Эндпоинты: `GET /api/testresult?launchId`, `GET /api/testresult/{id}`, `POST /api/testresult`,
`PATCH /api/testresult/{id}`, `DELETE /api/testresult/{id}`, `GET /api/testresult/{id}/history`,
`/api/testresult/{id}/step` (шаги результата), `/api/testresult/{id}/attachment`.

## 7. Справочники

| Ресурс | Эндпоинт | Схема | Зачем |
|---|---|---|---|
| Статусы | `GET /api/status?workflowId` | `StatusDto` (`id`, `name`, `color`) | `statusId` для кейса |
| Воркфлоу | `GET /api/workflow` | `WorkflowDto` (`id`, `name`, `statuses[]`) | `workflowId` |
| Схема воркфлоу | `GET /api/workflowschema?projectId&type` | `WorkflowSchemaDto` | какой воркфлоу у проекта |
| Слои | `GET /api/testlayer` | `TestLayerDto` (`id`, `name`) | `testLayerId` |
| Кастомные поля проекта | `GET /api/project/{projectId}/cf` | `CustomFieldDto` | `customFields[]` |
| Значения кастомных полей | `GET|POST /api/project/{projectId}/cfv` | `CustomFieldValueDto` | подстановка значений |
| Теги | `GET /api/tag` | `TestTagDto[]` (`id`, `name`) | `tags[]` (нужен `id`); ответ — **плоский массив**, без пагинации и без `query`, поэтому поиск по имени — на клиенте |
| Филтры | `GET /api/filter`, `/api/filter/suggest` | `FilterDto` | `filterId` в листингах |
| Дерево | `GET /api/testcasetree`, `/api/testcasetree/paths` | — | `leafsInclude`, `path` |

`GET /api/cf` (без проекта) — **deprecated**, использовать `/api/project/{projectId}/cf`.

## 8. Прогон выбранных кейсов

`POST /api/testcase/bulk/run/new` (и V2-двойник `POST /api/v2/test-case/bulk/run/new`).

Тело `TestCaseBulkRunNewLaunchDto`, required `launchName`, `selection`:

| Поле | Тип |
|---|---|
| `launchName` | string |
| `selection` | `TestCaseTreeSelectionDto` |
| `assignees[]` | string[] (логины) |
| `assignmentStrategy` | `AssignmentTypeDto` |
| `envVarValueSets[]` | `EnvironmentSetDto` |
| `issues[]` | `IssueDto` |
| `jobsMapping[]`, `jobsParams[]` | маппинг джоб |
| `links[]`, `tags[]`, `releaseId` | как у `LaunchCreateDto` |

`TestCaseTreeSelectionDto`, required `projectId`:

| Поле | Тип | Смысл |
|---|---|---|
| `projectId` | int | проект |
| `leafsInclude[]` / `leafsExclude[]` | int[] | **кейсы по id** — именно `leafsInclude`, поля `leafIds` не существует |
| `groupsInclude[]` / `groupsExclude[]` | int[][] | папки дерева |
| `path[]` | int[] | путь в дереве |
| `treeId` | int | дерево |
| `search` | string | текстовый поиск |
| `filterId` | int | сохранённый фильтр (вместо перечисления) |
| `inverted` | bool | инвертировать выбор |
| `jobId` | int | выбор из джоба |
| `deleted` | bool | включать удалённые |

Похожие bulk-операции по кейсам (не выводим в инструменты, доступны через `api_request`):
`/api/testcase/bulk/run/existing` (в существующий запуск), `/bulk/run/distribution-preview`,
`/bulk/move`, `/bulk/remove`, `/bulk/clone`, `/bulk/tag/add|remove`, `/bulk/status/set`,
`/bulk/testplan/create`, `/bulk/cfv/add|remove`, `/bulk/layer/set`, `/bulk/mute/add`.

## 9. Вложения

| Область | Эндпоинты |
|---|---|
| Кейс | `GET|POST /api/testcase/attachment`, `PATCH|DELETE /{id}`, `GET|PUT /{id}/content` |
| Результат | `GET|POST /api/testresult/attachment`, `PATCH|DELETE /{id}`, `GET|PUT /{id}/content` |
| Общий шаг | `GET|POST /api/sharedstep/attachment`, `PATCH|DELETE /{id}`, `GET|PUT /{id}/content` |
| Загрузка прогона | `POST /api/launch/{launchId}/upload[/archive|/file]`, `POST /api/upload?id=` (multipart, `202`) |

Формат ответа на `POST /api/testcase/attachment` — `TestCaseAttachmentDto` с `id`; содержимое кладётся
отдельным `PUT /{id}/content`. Точные тела multipart-эндпоинтов — в `api-inventory.md`.
