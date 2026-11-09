# Инвентарь эндпоинтов allure-testops-service 527u04

Всего путей: 634; операций: 845. Сгенерировано из `api-docs.json`.

Разбивка по первому сегменту пути:

| Префикс | Операций |
|---|---|
| `/testcase` | 101 |
| `/testresult` | 58 |
| `/integration` | 55 |
| `/launch` | 55 |
| `/v2` | 46 |
| `/project` | 37 |
| `/sharedstep` | 22 |
| `/account` | 19 |
| `/defect` | 19 |
| `/admin` | 18 |
| `/testplan` | 17 |
| `/tree-folder` | 14 |
| `/accessgroup` | 13 |
| `/testcasetree` | 13 |
| `/job` | 12 |
| `/export` | 11 |
| `/cfv` | 10 |
| `/mfa` | 10 |
| `/cf` | 9 |
| `/invite` | 9 |
| `/analytic` | 8 |
| `/cfproject` | 8 |
| `/dashboard` | 8 |
| `/filter` | 8 |
| `/notification` | 8 |
| `/upload` | 8 |
| `/environment` | 7 |
| `/ev` | 7 |
| `/release` | 7 |
| `/storage` | 7 |
| `/cfschema` | 6 |
| `/cleanerschema` | 6 |
| `/email-verification` | 6 |
| `/evv` | 6 |
| `/issue` | 6 |
| `/jobrun` | 6 |
| `/member` | 6 |
| `/permissionset` | 6 |
| `/projectsettings` | 6 |
| `/role` | 6 |
| `/security` | 6 |
| `/status` | 6 |
| `/tag` | 6 |
| `/testfixtureresult` | 6 |
| `/testlayer` | 6 |
| `/tree` | 6 |
| `/widget` | 6 |
| `/workflow` | 6 |
| `/category` | 5 |
| `/comment` | 5 |
| `/evschema` | 5 |
| `/globalsettings` | 5 |
| `/issueschema` | 5 |
| `/projectproperty` | 5 |
| `/roleschema` | 5 |
| `/testcaseupdateschema` | 5 |
| `/testkeyschema` | 5 |
| `/testlayerschema` | 5 |
| `/workflowschema` | 5 |
| `/categorymatcher` | 4 |
| `/cleanup` | 4 |
| `/importrequest` | 4 |
| `/testresulttree` | 4 |
| `/treepath` | 4 |
| `/login` | 3 |
| `/migration` | 3 |
| `/mute` | 3 |
| `/requirement` | 3 |
| `/token` | 3 |
| `/avatar` | 2 |
| `/cfbulk` | 2 |
| `/cfvbulk` | 2 |
| `/dashboard-template` | 2 |
| `/feature-flag` | 2 |
| `/license` | 2 |
| `/md` | 2 |
| `/alert` | 1 |
| `/business-metric` | 1 |
| `/inject` | 1 |
| `/misc` | 1 |
| `/permission` | 1 |
| `/register` | 1 |
| `/testkey` | 1 |
| `/update-testcase-duration` | 1 |
| `/user` | 1 |

## /accessgroup — 13 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/accessgroup` | Find all groups | access-group-controller |
| POST | `/api/accessgroup` | Create a new group | access-group-controller |
| POST | `/api/accessgroup/bulk/delete` | Bulk delete teams | access-group-bulk-controller |
| GET | `/api/accessgroup/suggest` | Suggests groups | access-group-controller |
| DELETE | `/api/accessgroup/{id}` | Delete group by id | access-group-controller |
| GET | `/api/accessgroup/{id}` | Find group by id | access-group-controller |
| PATCH | `/api/accessgroup/{id}` | Patch group | access-group-controller |
| DELETE | `/api/accessgroup/{id}/project` | Delete projects from group | access-group-controller |
| GET | `/api/accessgroup/{id}/project` | Get group's projects | access-group-controller |
| POST | `/api/accessgroup/{id}/project` | Add projects to group | access-group-controller |
| DELETE | `/api/accessgroup/{id}/user` | Delete users from group | access-group-controller |
| GET | `/api/accessgroup/{id}/user` | Get group's users | access-group-controller |
| POST | `/api/accessgroup/{id}/user` | Add users to group | access-group-controller |

## /account — 19 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/account` | Find all accounts | account-admin-controller |
| GET | `/api/account/feature-flag/me` | Get feature flags for current account | feature-flag-controller |
| GET | `/api/account/me` | Get current user's account | account-user-controller |
| POST | `/api/account/password` | Change your account password | account-user-controller |
| POST | `/api/account/password/forgot` | Restore account password by email | account-user-controller |
| POST | `/api/account/password/reset` | Reset account password | account-user-controller |
| POST | `/api/account/password/resetbyemail` | Reset current password | account-user-controller |
| POST | `/api/account/register` | Register new account | account-admin-controller |
| DELETE | `/api/account/{accountId}` | delete account authority | account-admin-controller |
| POST | `/api/account/{accountId}/authority` | Set account authorities *(deprecated)* | account-admin-controller |
| GET | `/api/account/{accountId}/feature-flag` | Get feature flags by accountId | feature-flag-controller |
| PUT | `/api/account/{accountId}/feature-flag/{featureFlagName}` | Set feature flag for account | feature-flag-controller |
| POST | `/api/account/{accountId}/password/reset` | Reset the password for account | account-admin-controller |
| POST | `/api/account/{accountId}/password/send` | Send the password to user | account-admin-controller |
| GET | `/api/account/{id}` | Get user's account by id or username | account-user-controller |
| PATCH | `/api/account/{id}` | Patch account | account-user-controller |
| POST | `/api/account/{id}/approve` | Approve/refuse account *(deprecated)* | account-admin-controller |
| POST | `/api/account/{id}/enable` | Enabled/disable account *(deprecated)* | account-admin-controller |
| GET | `/api/account/{id}/find` | Get user's account by id or username | account-admin-controller |

## /admin — 18 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/admin/account` | Get member by username | account-management-controller |
| POST | `/api/admin/account/bulk/activate` | Bulk activate accounts | account-management-bulk-controller |
| POST | `/api/admin/account/bulk/deactivate` | Bulk deactivate account | account-management-bulk-controller |
| POST | `/api/admin/account/bulk/role` | Bulk change role | account-management-bulk-controller |
| GET | `/api/admin/account/deactivated` | Get deactivated accounts | account-management-controller |
| POST | `/api/admin/account/feature/grant` | Bulk grant feature permission to accounts | account-feature-controller |
| POST | `/api/admin/account/feature/revoke` | Bulk revoke feature permission from accounts | account-feature-controller |
| GET | `/api/admin/account/guest` | Get guest list | account-management-controller |
| GET | `/api/admin/account/info` | Get info about tabs and licenses | account-management-controller |
| GET | `/api/admin/account/member` | Get members list | account-management-controller |
| GET | `/api/admin/account/suggest` | Get list of members and guests | account-management-controller |
| PATCH | `/api/admin/account/{id}` | Edit account profile | account-management-controller |
| POST | `/api/admin/account/{id}/activate` | Activate account | account-management-controller |
| POST | `/api/admin/account/{id}/deactivate` | Deactivate account | account-management-controller |
| GET | `/api/admin/account/{id}/feature` | Get account feature permissions | account-feature-controller |
| DELETE | `/api/admin/account/{id}/feature/{featureKey}` | Revoke feature permission from account | account-feature-controller |
| POST | `/api/admin/account/{id}/feature/{featureKey}` | Grant feature permission to account | account-feature-controller |
| POST | `/api/admin/account/{id}/role` | Change account role | account-management-controller |

## /alert — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/alert/state` | Returns global alert state for the current user | alert-state-controller |

## /analytic — 8 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/analytic/{id}/automation_chart` |  | analytic-controller |
| GET | `/api/analytic/{id}/group_by_automation` |  | analytic-controller |
| GET | `/api/analytic/{id}/group_by_status` |  | analytic-controller |
| GET | `/api/analytic/{id}/launch_duration_histogram` |  | analytic-controller |
| GET | `/api/analytic/{id}/mute_trend` |  | analytic-controller |
| GET | `/api/analytic/{id}/statistic_trend` |  | analytic-controller |
| GET | `/api/analytic/{id}/tc_last_result` |  | analytic-controller |
| GET | `/api/analytic/{id}/tc_success_rate` |  | analytic-controller |

## /avatar — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/avatar/{username}` |  | avatar-controller |
| POST | `/api/avatar/{username}` |  | avatar-controller |

## /business-metric — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/business-metric` | Find all business metrics | business-metric-controller |

## /category — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/category` |  | category-controller |
| POST | `/api/category` |  | category-controller |
| GET | `/api/category/suggest` |  | category-controller |
| DELETE | `/api/category/{id}` |  | category-controller |
| PATCH | `/api/category/{id}` |  | category-controller |

## /categorymatcher — 4 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/categorymatcher` |  | category-matcher-controller |
| POST | `/api/categorymatcher` |  | category-matcher-controller |
| DELETE | `/api/categorymatcher/{id}` |  | category-matcher-controller |
| PATCH | `/api/categorymatcher/{id}` |  | category-matcher-controller |

## /cf — 9 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/cf` | Deprecated. Use GET /api/project/{projectId}/cf instead *(deprecated)* | custom-field-controller |
| POST | `/api/cf` |  | custom-field-controller |
| GET | `/api/cf/count-usage` | Count custom fields usage in projects | custom-field-controller |
| POST | `/api/cf/merge` |  | custom-field-controller |
| GET | `/api/cf/suggest` |  | custom-field-controller |
| DELETE | `/api/cf/{id}` |  | custom-field-controller |
| GET | `/api/cf/{id}` |  | custom-field-controller |
| PATCH | `/api/cf/{id}` |  | custom-field-controller |
| POST | `/api/cf/{id}/archived` | Soft delete custom field | custom-field-controller |

## /cfbulk — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/cfbulk/add-to-projects` | Add custom fields to projects | custom-field-bulk-controller |
| POST | `/api/cfbulk/archive` | Archive/restore custom fields | custom-field-bulk-controller |

## /cfproject — 8 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/cfproject` |  | custom-field-project-controller |
| POST | `/api/cfproject/add` | Add custom field to projects | custom-field-project-controller |
| POST | `/api/cfproject/add-to-project` | Add custom fields to project | custom-field-project-controller |
| POST | `/api/cfproject/default` | Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead *(deprecated)* | custom-field-project-controller |
| POST | `/api/cfproject/delta` | Find missing custom fields | custom-field-project-controller |
| GET | `/api/cfproject/in-projects` | Find projects that use specified custom field | custom-field-project-controller |
| DELETE | `/api/cfproject/remove` | Remove custom field from project | custom-field-project-controller |
| POST | `/api/cfproject/required` | Deprecated. Use PATCH /api/project/{projectId}/cf/{cfId} instead *(deprecated)* | custom-field-project-controller |

## /cfschema — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/cfschema` | Find all custom field schemas for specified project and custom field | custom-field-schema-controller |
| POST | `/api/cfschema` | Create a new custom field schema | custom-field-schema-controller |
| GET | `/api/cfschema/count-mappings` | Count custom fields mappings | custom-field-schema-controller |
| DELETE | `/api/cfschema/{id}` | Delete custom field schema by id | custom-field-schema-controller |
| GET | `/api/cfschema/{id}` | Find custom field schema by id | custom-field-schema-controller |
| PATCH | `/api/cfschema/{id}` | Patch custom field schema | custom-field-schema-controller |

## /cfv — 10 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/cfv` | Find all custom field values | custom-field-value-controller |
| POST | `/api/cfv` | Deprecated. Use POST /api/project/{projectId}/cfv instead *(deprecated)* | custom-field-value-controller |
| POST | `/api/cfv/merge` | Merge project custom field values into new global | custom-field-value-controller |
| POST | `/api/cfv/merge-to/{toCfvId}` | Merge project custom field values into existing global | custom-field-value-controller |
| GET | `/api/cfv/suggest` | Suggest custom field values | custom-field-value-controller |
| GET | `/api/cfv/suggest/{projectId}` | Suggest custom field values | custom-field-value-controller |
| DELETE | `/api/cfv/{id}` | Delete custom field value by id | custom-field-value-controller |
| GET | `/api/cfv/{id}` | Find custom field value by id | custom-field-value-controller |
| PATCH | `/api/cfv/{id}` | Patch custom field value | custom-field-value-controller |
| POST | `/api/cfv/{id}/rename` | Deprecated. Use PUT /api/project/{projectId}/cfv/{cvfId}/name instead *(deprecated)* | custom-field-value-controller |

## /cfvbulk — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| DELETE | `/api/cfvbulk/delete` | Delete custom field values from project | custom-field-value-bulk-controller |
| POST | `/api/cfvbulk/merge` | Deprecated. Use POST /api/cfv/merge-by-name or /api/cfv/merge-by-id instead *(deprecated)* | custom-field-value-bulk-controller |

## /cleanerschema — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/cleanerschema` | Find all cleaner schemas for given project | cleaner-schema-controller |
| POST | `/api/cleanerschema` | Create a new cleaner schema | cleaner-schema-controller |
| GET | `/api/cleanerschema/global` | Find all global cleaner schemas | cleaner-schema-controller |
| DELETE | `/api/cleanerschema/{id}` | Delete cleaner schema by id | cleaner-schema-controller |
| GET | `/api/cleanerschema/{id}` | Find cleaner schema by id | cleaner-schema-controller |
| PATCH | `/api/cleanerschema/{id}` | Patch cleaner schema | cleaner-schema-controller |

## /cleanup — 4 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/cleanup/launch` |  | cleanup-controller |
| POST | `/api/cleanup/scheduler/blob_remove_task` |  | cleanup-controller |
| POST | `/api/cleanup/scheduler/cleaner_schema_global` |  | cleanup-controller |
| POST | `/api/cleanup/scheduler/cleaner_schema_project` |  | cleanup-controller |

## /comment — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/comment` | Find all comments | comment-controller |
| POST | `/api/comment` | Create a new comment | comment-controller |
| DELETE | `/api/comment/{id}` | Delete comment by id | comment-controller |
| GET | `/api/comment/{id}` | Find comment by id | comment-controller |
| PATCH | `/api/comment/{id}` | Dynamic update comment | comment-controller |

## /dashboard — 8 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/dashboard` |  | dashboard-controller |
| POST | `/api/dashboard` |  | dashboard-controller |
| DELETE | `/api/dashboard/{id}` |  | dashboard-controller |
| GET | `/api/dashboard/{id}` |  | dashboard-controller |
| PATCH | `/api/dashboard/{id}` |  | dashboard-controller |
| PUT | `/api/dashboard/{id}` |  | dashboard-controller |
| POST | `/api/dashboard/{id}/copy` |  | dashboard-controller |
| POST | `/api/dashboard/{id}/drag-and-drop` |  | dashboard-controller |

## /dashboard-template — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/dashboard-template` |  | dashboard-template-controller |
| GET | `/api/dashboard-template/{id}` |  | dashboard-template-controller |

## /defect — 19 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/defect` |  | defect-controller |
| POST | `/api/defect` |  | defect-controller |
| POST | `/api/defect/bulk/close` |  | defect-bulk-controller |
| POST | `/api/defect/bulk/remove` |  | defect-bulk-controller |
| POST | `/api/defect/bulk/reopen` |  | defect-bulk-controller |
| POST | `/api/defect/matcher` |  | defect-matcher-controller |
| DELETE | `/api/defect/matcher/{id}` |  | defect-matcher-controller |
| PATCH | `/api/defect/matcher/{id}` |  | defect-matcher-controller |
| GET | `/api/defect/suggest` |  | defect-controller |
| DELETE | `/api/defect/{id}` |  | defect-controller |
| GET | `/api/defect/{id}` |  | defect-controller |
| PATCH | `/api/defect/{id}` |  | defect-controller |
| POST | `/api/defect/{id}/createissue` |  | defect-controller |
| DELETE | `/api/defect/{id}/issue` |  | defect-controller |
| POST | `/api/defect/{id}/issue` |  | defect-controller |
| GET | `/api/defect/{id}/launch` |  | defect-controller |
| GET | `/api/defect/{id}/matcher` |  | defect-controller |
| GET | `/api/defect/{id}/testcase` |  | defect-controller |
| GET | `/api/defect/{id}/testresult` |  | defect-controller |

## /email-verification — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/email-verification/token/validate` | Validate mail change token | mail-verification-controller |
| POST | `/api/email-verification/verify` | Verify email | mail-verification-controller |
| GET | `/api/email-verification/{userId}` | Get email change confirmation info | mail-verification-controller |
| PATCH | `/api/email-verification/{userId}` | Edit email in mail confirmation token or send link to new email | mail-verification-controller |
| POST | `/api/email-verification/{userId}/cancel` | Cancel email change | mail-verification-controller |
| POST | `/api/email-verification/{userId}/resend` | Resend email verification link | mail-verification-controller |

## /environment — 7 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/environment` | Find all environment variables | env-var-controller |
| POST | `/api/environment` | Create a new environment variable | env-var-controller |
| POST | `/api/environment/merge` | Merge environment variables | env-var-controller |
| GET | `/api/environment/suggest` | Suggest environment variables | env-var-controller |
| DELETE | `/api/environment/{id}` | Delete environment variable by id | env-var-controller |
| GET | `/api/environment/{id}` | Find environment variable by id | env-var-controller |
| PATCH | `/api/environment/{id}` | Patch environment variable | env-var-controller |

## /ev — 7 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/ev` | Find all environment variables | env-var-controller |
| POST | `/api/ev` | Create a new environment variable | env-var-controller |
| POST | `/api/ev/merge` | Merge environment variables | env-var-controller |
| GET | `/api/ev/suggest` | Suggest environment variables | env-var-controller |
| DELETE | `/api/ev/{id}` | Delete environment variable by id | env-var-controller |
| GET | `/api/ev/{id}` | Find environment variable by id | env-var-controller |
| PATCH | `/api/ev/{id}` | Patch environment variable | env-var-controller |

## /evschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/evschema` | Find all env var schemas for given project | env-var-schema-controller |
| POST | `/api/evschema` | Create a new env var schema | env-var-schema-controller |
| DELETE | `/api/evschema/{id}` | Delete env var schema by id | env-var-schema-controller |
| GET | `/api/evschema/{id}` | Find env var schema by id | env-var-schema-controller |
| PATCH | `/api/evschema/{id}` | Patch env var schema | env-var-schema-controller |

## /evv — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/evv` | Find all environment values | env-var-value-controller |
| POST | `/api/evv` | Create a new environment value | env-var-value-controller |
| GET | `/api/evv/suggest` | Suggest environment values | env-var-value-controller |
| DELETE | `/api/evv/{id}` | Delete environment value by id | env-var-value-controller |
| GET | `/api/evv/{id}` | Find environment value by id | env-var-value-controller |
| PATCH | `/api/evv/{id}` | Patch environment value | env-var-value-controller |

## /export — 11 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/export` | Find all reports | export-request-controller |
| GET | `/api/export/download/{exportRequestId}` | Download prepared export | export-request-controller |
| POST | `/api/export/launch/pdf` | Generate launch pdf report | export-controller |
| GET | `/api/export/launch/pdf/structure` | Get supported launch pdf report parts | export-controller |
| POST | `/api/export/testcase/csv` | Generate test cases csv report | export-controller |
| GET | `/api/export/testcase/csv/mapping` | Get supported test case export fields | export-controller |
| POST | `/api/export/testcase/pdf` | Generate test cases pdf report | export-controller |
| POST | `/api/export/testresult/csv` | Generate test results csv report | export-controller |
| GET | `/api/export/testresult/csv/mapping` | Get supported test result export fields | export-controller |
| DELETE | `/api/export/{id}` | Delete report | export-request-controller |
| GET | `/api/export/{id}` | Find report by id | export-request-controller |

## /feature-flag — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/feature-flag` | Add new feature flag | feature-flag-controller |
| PUT | `/api/feature-flag/{featureFlagName}` | Set feature flag for all accounts | feature-flag-controller |

## /filter — 8 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/filter` | Find all filters by given project | filter-controller |
| POST | `/api/filter` | Create a new filter | filter-controller |
| GET | `/api/filter/base` | Get default filter | filter-controller |
| POST | `/api/filter/base` | Set filter as default | filter-controller |
| GET | `/api/filter/suggest` | Get suggest for filters | filter-controller |
| DELETE | `/api/filter/{id}` | Delete filter by id | filter-controller |
| GET | `/api/filter/{id}` | Find filter by id | filter-controller |
| PATCH | `/api/filter/{id}` | Patch filter | filter-controller |

## /globalsettings — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/globalsettings` | Returns global settings | global-settings-controller |
| GET | `/api/globalsettings/globalpermissions` | Returns all global permissions for user | global-settings-controller |
| GET | `/api/globalsettings/mfa` | Returns mfa settings | global-settings-controller |
| PATCH | `/api/globalsettings/mfa` | Patch MFA global settings | global-settings-controller |
| PATCH | `/api/globalsettings/projectcreate` | Patch global settings | global-settings-controller |

## /importrequest — 4 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/importrequest` | Find all imports | import-request-controller |
| POST | `/api/importrequest` | Upload import file | import-request-controller |
| DELETE | `/api/importrequest/{id}` | Delete import | import-request-controller |
| GET | `/api/importrequest/{id}` | Find import by id | import-request-controller |

## /inject — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/inject/init.js` |  | inject-js-controller |

## /integration — 55 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/integration` |  | integration-controller |
| POST | `/api/integration` |  | integration-controller |
| GET | `/api/integration/account` |  | account-integration-controller |
| POST | `/api/integration/account` |  | account-integration-controller |
| GET | `/api/integration/account/available` |  | account-integration-controller |
| GET | `/api/integration/account/available/type` |  | account-integration-controller |
| GET | `/api/integration/account/secretfields` |  | account-integration-controller |
| GET | `/api/integration/account/type` |  | account-integration-controller |
| POST | `/api/integration/account/validate` |  | account-integration-controller |
| DELETE | `/api/integration/account/{integrationId}` |  | account-integration-controller |
| PATCH | `/api/integration/account/{integrationId}` |  | account-integration-controller |
| GET | `/api/integration/available` |  | integration-controller |
| GET | `/api/integration/errorlog` |  | integration-error-log-controller |
| GET | `/api/integration/errorlog/personal` |  | integration-error-log-controller |
| GET | `/api/integration/export` |  | integration-export-controller |
| POST | `/api/integration/export` |  | integration-export-controller |
| GET | `/api/integration/export/field` | Get export form fields for specified project integration | integration-export-controller |
| DELETE | `/api/integration/export/{id}` |  | integration-export-controller |
| GET | `/api/integration/export/{id}` |  | integration-export-controller |
| PATCH | `/api/integration/export/{id}` |  | integration-export-controller |
| GET | `/api/integration/globalfields` |  | integration-controller |
| GET | `/api/integration/issue/field` | Get available fields for specified project integration, project key and issue type | integration-issue-controller |
| GET | `/api/integration/issue/project` | Get available projects for specified project integration | integration-issue-controller |
| GET | `/api/integration/issue/suggest` | Get available issues for specified project integration | integration-issue-controller |
| GET | `/api/integration/issue/type` | Get available issue types for specified project integration and project key | integration-issue-controller |
| POST | `/api/integration/issue/{integrationId}/fixlinks` | Fix issue links without url | integration-issue-controller |
| POST | `/api/integration/project` |  | integration-controller |
| POST | `/api/integration/project/validate` |  | integration-controller |
| GET | `/api/integration/project/{projectId}` |  | integration-controller |
| GET | `/api/integration/project/{projectId}/available` |  | integration-controller |
| GET | `/api/integration/project/{projectId}/available/type` |  | integration-controller |
| GET | `/api/integration/project/{projectId}/type` |  | integration-controller |
| GET | `/api/integration/projectfields` |  | integration-controller |
| GET | `/api/integration/requirement/suggest` | Get available requirement for specified project integration | integration-requirement-link-controller |
| POST | `/api/integration/requirement/{integrationId}/fix-links` | Fix requirements without url | integration-requirement-link-controller |
| GET | `/api/integration/select` |  | integration-select-controller |
| GET | `/api/integration/suggest` | Suggest integrations | integration-controller |
| GET | `/api/integration/tms/projects` | Get available projects for tms | integration-tms-controller |
| GET | `/api/integration/type` |  | integration-controller |
| POST | `/api/integration/v2/project` |  | integration-controller |
| POST | `/api/integration/validate` |  | integration-controller |
| GET | `/api/integration/webhook` | Find all webhook configs for integration | integration-webhook-controller |
| POST | `/api/integration/webhook` | Create a new webhook config | integration-webhook-controller |
| GET | `/api/integration/webhook/log` | Find all webhook logs by integration or webhook | integration-webhook-controller |
| DELETE | `/api/integration/webhook/{id}` | Delete webhook config | integration-webhook-controller |
| PATCH | `/api/integration/webhook/{id}` | Patch webhook config | integration-webhook-controller |
| DELETE | `/api/integration/{id}` |  | integration-controller |
| GET | `/api/integration/{id}` |  | integration-controller |
| PATCH | `/api/integration/{id}` |  | integration-controller |
| POST | `/api/integration/{id}/credentials/policy-impact` |  | integration-controller |
| GET | `/api/integration/{id}/project` |  | integration-controller |
| GET | `/api/integration/{id}/project/available` |  | integration-controller |
| DELETE | `/api/integration/{integrationId}/project/{projectId}` |  | integration-controller |
| GET | `/api/integration/{integrationId}/project/{projectId}` |  | integration-controller |
| PATCH | `/api/integration/{integrationId}/project/{projectId}` |  | integration-controller |

## /invite — 9 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/invite` | Get invites list | invite-controller |
| POST | `/api/invite` | Send invite | invite-controller |
| POST | `/api/invite/bulk/cancel` | Bulk cancel invites | invite-bulk-controller |
| POST | `/api/invite/bulk/resend` | Bulk resend invites | invite-bulk-controller |
| POST | `/api/invite/token/validate` | Validate invite token | invite-controller |
| POST | `/api/invite/validate` | Validate invite email | invite-controller |
| PATCH | `/api/invite/{id}` | Edit invite | invite-controller |
| POST | `/api/invite/{id}/cancel` | Cancel invite | invite-controller |
| POST | `/api/invite/{id}/resend` | Resend invite | invite-controller |

## /issue — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/issue` | Find all issues | issue-controller |
| POST | `/api/issue` | Create a new issue | issue-controller |
| GET | `/api/issue/suggest` | Suggest issues | issue-controller |
| DELETE | `/api/issue/{id}` | Delete issue by id | issue-controller |
| GET | `/api/issue/{id}` | Find issue by id | issue-controller |
| PATCH | `/api/issue/{id}` | Patch issue schema | issue-controller |

## /issueschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/issueschema` | Find all issue schemas for given project | issue-schema-controller |
| POST | `/api/issueschema` | Create a new issue schema | issue-schema-controller |
| DELETE | `/api/issueschema/{id}` | Delete an issue schema by id | issue-schema-controller |
| GET | `/api/issueschema/{id}` | Find an issue schema by id | issue-schema-controller |
| PATCH | `/api/issueschema/{id}` | Patch an issue schema | issue-schema-controller |

## /job — 12 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/job` | Find job by given project and external id | job-controller |
| POST | `/api/job` | Create a new job | job-controller |
| GET | `/api/job/candidate` | Get suggest for job candidate | job-controller |
| GET | `/api/job/suggest` | Suggest for jobs | job-controller |
| DELETE | `/api/job/{id}` | Delete job by id | job-controller |
| GET | `/api/job/{id}` | Find job by id | job-controller |
| PATCH | `/api/job/{id}` | Patch job | job-controller |
| POST | `/api/job/{id}/run` | Run job to a new launch | job-controller |
| POST | `/api/job/{id}/sync` | Sync job with build server | job-controller |
| POST | `/api/job/{id}/tree-folder/run` | Run selected tree-folder test cases to a new launch | job-controller |
| GET | `/api/job/{id}/tree/group` | Find tree groups for node | job-controller |
| GET | `/api/job/{id}/tree/leaf` | Find tree leaves for node | job-controller |

## /jobrun — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/jobrun/{id}` | Get job run by id | job-run-controller |
| GET | `/api/jobrun/{id}/plan` | Find test plan for execution by external id | job-run-test-plan-controller |
| POST | `/api/jobrun/{id}/rerun` | Rerun job | job-run-controller |
| POST | `/api/jobrun/{id}/upload` | Manually upload job run results | job-run-controller |
| POST | `/api/jobrun/{id}/upload/archive` | Manually upload job run results | job-run-controller |
| POST | `/api/jobrun/{id}/upload/file` | Manually upload job run results | job-run-controller |

## /launch — 55 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/launch` | Find all launches preview | launch-controller |
| POST | `/api/launch` | Create a new launch | launch-controller |
| GET | `/api/launch/__search` | Find all launches by given AQL | launch-search-controller |
| GET | `/api/launch/diff/failed` | Find failed | launch-diff-controller |
| GET | `/api/launch/diff/fixed` | Find fixed | launch-diff-controller |
| GET | `/api/launch/diff/matrix` | Get status matrix for given launches with overlay parameter | launch-diff-controller |
| GET | `/api/launch/diff/missed` | Missed tests | launch-diff-controller |
| GET | `/api/launch/diff/new` | New tests | launch-diff-controller |
| GET | `/api/launch/diff/status-changed` | Find status changed difference | launch-diff-controller |
| GET | `/api/launch/issue` | Get all issues used in launches | launch-issue-controller |
| POST | `/api/launch/merge` | Merge launches | launch-controller |
| POST | `/api/launch/new` | Create a new launch via event | launch-controller |
| GET | `/api/launch/query/validate` | Find all launches by given AQL | launch-search-controller |
| GET | `/api/launch/suggest` | Suggest for launches | launch-controller |
| GET | `/api/launch/tag` | Find all tags | launch-tag-controller |
| POST | `/api/launch/tag` | Create a new Launch tag | launch-tag-controller |
| GET | `/api/launch/tag/suggest` | Suggest Launch Tags | launch-tag-controller |
| DELETE | `/api/launch/tag/{id}` | Delete Launch tag by id | launch-tag-controller |
| GET | `/api/launch/tag/{id}` | Find Launch tag by id | launch-tag-controller |
| PATCH | `/api/launch/tag/{id}` | Patch Launch tag | launch-tag-controller |
| POST | `/api/launch/upload` | Create launch from uploaded results | launch-upload-controller |
| DELETE | `/api/launch/{id}` | Delete launch by id | launch-controller |
| GET | `/api/launch/{id}` | Find launch by id | launch-controller |
| PATCH | `/api/launch/{id}` | Patch launch | launch-controller |
| GET | `/api/launch/{id}/assignees` | Get launch assignees | launch-controller |
| GET | `/api/launch/{id}/category` | Get launch error categories | launch-controller |
| POST | `/api/launch/{id}/close` | Close launch | launch-controller |
| POST | `/api/launch/{id}/copy` | Copy launch | launch-controller |
| GET | `/api/launch/{id}/defect` | Get launch defects | launch-controller |
| POST | `/api/launch/{id}/defect/apply` | Apply defect matchers to launch | launch-controller |
| GET | `/api/launch/{id}/duration` | Get launch duration | launch-controller |
| GET | `/api/launch/{id}/env` | Get launch environment | launch-controller |
| GET | `/api/launch/{id}/job` | Get launch jobs | launch-controller |
| GET | `/api/launch/{id}/job/suggest` | Suggest launch jobs | launch-controller |
| GET | `/api/launch/{id}/memberstats` | Get member stats widget data | launch-controller |
| GET | `/api/launch/{id}/muted` | Get muted test results | launch-controller |
| GET | `/api/launch/{id}/progress` | Get progress widget data | launch-controller |
| PATCH | `/api/launch/{id}/release` | Assign release to launch | launch-controller |
| POST | `/api/launch/{id}/reopen` | Reopen launch | launch-controller |
| GET | `/api/launch/{id}/requirementstats` | Get requirement stats widget data | launch-controller |
| GET | `/api/launch/{id}/retries` | Get retries widget data | launch-controller |
| GET | `/api/launch/{id}/statistic` | Get launch statistic | launch-controller |
| POST | `/api/launch/{id}/testcase/add` | Add test cases to launch | launch-controller |
| GET | `/api/launch/{id}/tester` | Get launch testers | launch-controller |
| POST | `/api/launch/{id}/testplan/add` | Add test plan to launch | launch-controller |
| POST | `/api/launch/{id}/tree-folder/testcase/add` | Add test cases from tree folders to launch | launch-controller |
| GET | `/api/launch/{id}/uncategorized` | Get uncategorized test results | launch-controller |
| GET | `/api/launch/{id}/unresolved` | Get unresolved test results | launch-controller |
| GET | `/api/launch/{id}/variables` | Get variables widget data | launch-controller |
| GET | `/api/launch/{id}/widget/flaky` | Get suites for tree data | launch-controller |
| GET | `/api/launch/{id}/widget/tree` |  | launch-controller |
| POST | `/api/launch/{launchId}/issue/export` | Export launch data to issue issueTracker | launch-issue-controller |
| POST | `/api/launch/{launchId}/upload` | Manually upload launch results | launch-upload-controller |
| POST | `/api/launch/{launchId}/upload/archive` | Manually upload launch results | launch-upload-controller |
| POST | `/api/launch/{launchId}/upload/file` | Manually upload launch results | launch-upload-controller |

## /license — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/license` | Returns application license | license-controller |
| POST | `/api/license` | Set license | license-controller |

## /login — 3 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/login/invite-personal` |  | invite-login-controller |
| GET | `/api/login/props` |  | authentication-controller |
| POST | `/api/login/system` | System login | login |

## /md — 2 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/md/preview` | Converts markdown text to html | markdown-preview-controller |
| POST | `/api/md/preview` | Converts markdown text to html | markdown-preview-controller |

## /member — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/member` | Find all role users | member-controller |
| POST | `/api/member` | Create a new role user | member-controller |
| GET | `/api/member/suggest` | Suggest members | member-controller |
| DELETE | `/api/member/{id}` | Delete role user by id | member-controller |
| GET | `/api/member/{id}` | Find role user by id | member-controller |
| PATCH | `/api/member/{id}` | Patch role user | member-controller |

## /mfa — 10 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/mfa/backup-codes` |  | mfa-controller |
| GET | `/api/mfa/backup-codes/count` |  | mfa-controller |
| POST | `/api/mfa/confirm-settings` |  | mfa-controller |
| POST | `/api/mfa/disable/user` |  | mfa-controller |
| POST | `/api/mfa/enable/user` |  | mfa-controller |
| POST | `/api/mfa/generate/backup-codes` |  | mfa-controller |
| POST | `/api/mfa/generate/init-settings` |  | mfa-controller |
| POST | `/api/mfa/reset/settings/{userID}` |  | mfa-controller |
| GET | `/api/mfa/status` |  | mfa-controller |
| POST | `/api/mfa/verify` |  | mfa-controller |

## /migration — 3 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/migration/job` | Find migration jobs | async-job-controller |
| GET | `/api/migration/job/{jobId}` | Get the specified migration job by id including its steps | async-job-controller |
| POST | `/api/migration/job/{jobId}/cancel` | Cancel the specified migration job | async-job-controller |

## /misc — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/misc/session-stat` | Find accounts and enrich them by last session date in Redis cache if exists | admin-misc-controller |

## /mute — 3 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/mute` | Find all mutes for test case | mute-controller |
| POST | `/api/mute` | Create a new mute | mute-controller |
| DELETE | `/api/mute/{id}` | Delete mute | mute-controller |

## /notification — 8 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/notification/webhook` | Find webhooks in project | webhook-controller |
| POST | `/api/notification/webhook` |  | webhook-controller |
| POST | `/api/notification/webhook/validate` |  | webhook-controller |
| DELETE | `/api/notification/webhook/{id}` |  | webhook-controller |
| GET | `/api/notification/webhook/{id}` | Find webhook by given id | webhook-controller |
| PATCH | `/api/notification/webhook/{id}` |  | webhook-controller |
| POST | `/api/notification/webhook/{id}/disable` | Disable webhook by given id | webhook-controller |
| POST | `/api/notification/webhook/{id}/enable` | Enable webhook by given id | webhook-controller |

## /permission — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/permission` | Get user permissions for project | permission-controller |

## /permissionset — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/permissionset` | Find all permission sets | permission-set-controller |
| POST | `/api/permissionset` | Create a new permission set | permission-set-controller |
| GET | `/api/permissionset/suggest` | Suggests permission sets | permission-set-controller |
| DELETE | `/api/permissionset/{id}` | Delete permission set by id | permission-set-controller |
| GET | `/api/permissionset/{id}` | Find permission set by id | permission-set-controller |
| PATCH | `/api/permissionset/{id}` | Patch permission set | permission-set-controller |

## /project — 37 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/project` | Find all projects | project-controller |
| POST | `/api/project` | Create a new project | project-controller |
| DELETE | `/api/project/access/{projectId}/collaborator` | Delete collaborators from project | project-access-controller |
| GET | `/api/project/access/{projectId}/collaborator` | Get project collaborators | project-access-controller |
| POST | `/api/project/access/{projectId}/collaborator` | Add collaborators to project | project-access-controller |
| DELETE | `/api/project/access/{projectId}/group` | Delete groups from project | project-access-controller |
| GET | `/api/project/access/{projectId}/group` | Get project access groups | project-access-controller |
| POST | `/api/project/access/{projectId}/group` | Add groups to project | project-access-controller |
| GET | `/api/project/collaborator/suggest` | Find all collaborators across all accessible projects | project-collaborator-controller |
| GET | `/api/project/count-test-cases` | Count test cases in projects that use specified custom field | project-controller |
| GET | `/api/project/customfield` | Find projects that use/do not use specified custom field | project-controller |
| GET | `/api/project/owner/suggest` | Find all project owners across all accessible projects | project-collaborator-controller |
| GET | `/api/project/suggest` | Suggest projects | project-controller |
| DELETE | `/api/project/{id}` | Delete project by id | project-controller |
| GET | `/api/project/{id}` | Find project by id | project-controller |
| PATCH | `/api/project/{id}` | Patch project | project-controller |
| GET | `/api/project/{id}/assignee/suggest` | Suggest project members eligible to be test run assignees, not read-only | project-collaborator-controller |
| GET | `/api/project/{id}/business-metric` | Find specific project metric for the period | project-metric-controller |
| GET | `/api/project/{id}/collaborator` | Find all permission sets | project-collaborator-controller |
| POST | `/api/project/{id}/favorite` | Mark project as favorite | project-controller |
| GET | `/api/project/{id}/owner` | Find project owners | project-collaborator-controller |
| GET | `/api/project/{id}/stats` | Find project stats by id | project-controller |
| GET | `/api/project/{id}/suggest` | Find all collaborators; the user with priorityUserId will be placed first in the list | project-collaborator-controller |
| GET | `/api/project/{projectId}/category` |  | project-category-controller |
| POST | `/api/project/{projectId}/category` |  | project-category-controller |
| POST | `/api/project/{projectId}/category/remove` |  | project-category-controller |
| GET | `/api/project/{projectId}/categorymatcher` |  | project-category-matcher-controller |
| POST | `/api/project/{projectId}/categorymatcher` |  | project-category-matcher-controller |
| POST | `/api/project/{projectId}/categorymatcher/remove` |  | project-category-matcher-controller |
| GET | `/api/project/{projectId}/cf` | Find custom fields used in specified project | custom-field-project-controller-v-2 |
| PATCH | `/api/project/{projectId}/cf/{cfId}` |  | custom-field-project-controller-v-2 |
| GET | `/api/project/{projectId}/cfv` | Find all custom field values for specified project | custom-field-value-project-controller |
| POST | `/api/project/{projectId}/cfv` | Create a new custom field value for specified project | custom-field-value-project-controller |
| POST | `/api/project/{projectId}/cfv/merge` | Merge custom field values to new record | custom-field-value-project-controller |
| POST | `/api/project/{projectId}/cfv/merge-to/{toCfvId}` | Merge custom field values to existing record by id | custom-field-value-project-controller |
| PATCH | `/api/project/{projectId}/cfv/{cfvId}` | Patch specified custom field value, test results won't be affected | custom-field-value-project-controller |
| DELETE | `/api/project/{projectId}/cfv/{id}` | Delete specified custom field value for specified project | custom-field-value-project-controller |

## /projectproperty — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/projectproperty` | Find all project properties | project-property-controller |
| POST | `/api/projectproperty` | Create a new project property | project-property-controller |
| DELETE | `/api/projectproperty/{id}` | Delete project by id | project-property-controller |
| GET | `/api/projectproperty/{id}` | Find project property by id | project-property-controller |
| PATCH | `/api/projectproperty/{id}` | Patch project property | project-property-controller |

## /projectsettings — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/projectsettings/flaky` | Get flaky detection config | project-settings-controller |
| PATCH | `/api/projectsettings/flaky` | Save flaky detection config | project-settings-controller |
| GET | `/api/projectsettings/launchclose` | Get launch close config | project-settings-controller |
| PATCH | `/api/projectsettings/launchclose` | Save launch close config | project-settings-controller |
| GET | `/api/projectsettings/launchlivedoc` | Get launch live documentation config | project-settings-controller |
| PATCH | `/api/projectsettings/launchlivedoc` | Save launch live documentation config | project-settings-controller |

## /register — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/register` | Register a new user | registration-controller |

## /release — 7 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/release/compare` | Get status matrix for all the launches assigned to given release with overlay parameter | release-controller |
| POST | `/api/release/create` | Create a new release | release-controller |
| GET | `/api/release/findAll` | Find all releases by project | release-controller |
| GET | `/api/release/suggest` | Suggest releases | release-controller |
| GET | `/api/release/{id}` | Find release by id | release-controller |
| PATCH | `/api/release/{id}` | Update release (rename, close/open, delete/restore) | release-controller |
| POST | `/api/release/{id}/add-launches` | Assign launches to release | release-controller |

## /requirement — 3 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/requirement/suggest` | Suggest requirements | requirement-controller |
| DELETE | `/api/requirement/{id}` | Delete requirement link by id | requirement-controller |
| GET | `/api/requirement/{id}` | Find requirement link by id | requirement-controller |

## /role — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/role` | Find all roles | role-controller |
| POST | `/api/role` | Create a new role | role-controller |
| GET | `/api/role/suggest` | Suggest roles | role-controller |
| DELETE | `/api/role/{id}` | Delete role by id | role-controller |
| GET | `/api/role/{id}` | Find role by id | role-controller |
| PATCH | `/api/role/{id}` | Patch a role | role-controller |

## /roleschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/roleschema` | Find all role schemas for given project | role-schema-controller |
| POST | `/api/roleschema` | Create a new role schema | role-schema-controller |
| DELETE | `/api/roleschema/{id}` | Delete role schema by id | role-schema-controller |
| GET | `/api/roleschema/{id}` | Find role schema by id | role-schema-controller |
| PATCH | `/api/roleschema/{id}` | Patch role schema | role-schema-controller |

## /security — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/security/auth-providers` | Find all security auth providers | security-auth-provider-controller |
| POST | `/api/security/auth-providers` | Create a new security auth provider | security-auth-provider-controller |
| GET | `/api/security/auth-providers/{id}` | Find security auth provider by given id | security-auth-provider-controller |
| PATCH | `/api/security/auth-providers/{id}` | Update the security auth provider by given id | security-auth-provider-controller |
| POST | `/api/security/auth-providers/{id}/disable` | Disable security auth provider by given id | security-auth-provider-controller |
| POST | `/api/security/auth-providers/{id}/enable` | Enable security auth provider by given id | security-auth-provider-controller |

## /sharedstep — 22 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/sharedstep` | Find all shared steps for specified project | shared-step-controller |
| POST | `/api/sharedstep` | Create a new shared step | shared-step-controller |
| GET | `/api/sharedstep/attachment` | Find attachments for shared step | shared-step-attachment-controller |
| POST | `/api/sharedstep/attachment` | Upload new shared step attachments | shared-step-attachment-controller |
| DELETE | `/api/sharedstep/attachment/{id}` | Delete shared step attachment | shared-step-attachment-controller |
| PATCH | `/api/sharedstep/attachment/{id}` | Patch shared step attachment | shared-step-attachment-controller |
| GET | `/api/sharedstep/attachment/{id}/content` | Get attachment content by id | shared-step-attachment-controller |
| PUT | `/api/sharedstep/attachment/{id}/content` | Update shared step attachment content | shared-step-attachment-controller |
| POST | `/api/sharedstep/step` | Create scenario step | shared-step-scenario-controller |
| DELETE | `/api/sharedstep/step/{id}` | Delete a specified scenario step | shared-step-scenario-controller |
| PATCH | `/api/sharedstep/step/{id}` | Patch a specified scenario step | shared-step-scenario-controller |
| POST | `/api/sharedstep/step/{id}/copy` | Copy scenario step | shared-step-scenario-controller |
| POST | `/api/sharedstep/step/{id}/move` | Move scenario step | shared-step-scenario-controller |
| DELETE | `/api/sharedstep/{id}` | Delete shared step by id | shared-step-controller |
| GET | `/api/sharedstep/{id}` | Find shared step by id | shared-step-controller |
| PATCH | `/api/sharedstep/{id}` | Patch a specified shared step | shared-step-controller |
| POST | `/api/sharedstep/{id}/archive` | Archive ths shared step | shared-step-controller |
| DELETE | `/api/sharedstep/{id}/scenario` | Delete scenario for test case | shared-step-scenario-controller |
| POST | `/api/sharedstep/{id}/scenario` | Set new scenario for ss | shared-step-scenario-controller |
| GET | `/api/sharedstep/{id}/step` | Get scenario for shared step | shared-step-scenario-controller |
| POST | `/api/sharedstep/{id}/unarchive` | Unarchive ths shared step | shared-step-controller |
| GET | `/api/sharedstep/{id}/usage` | Get testcases with usage of shared step | shared-step-scenario-controller |

## /status — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/status` | Find all statuses | status-controller |
| POST | `/api/status` | Create a new status | status-controller |
| GET | `/api/status/suggest` | Suggest statuses | status-controller |
| DELETE | `/api/status/{id}` | Delete status by id | status-controller |
| GET | `/api/status/{id}` | Find status by id | status-controller |
| PATCH | `/api/status/{id}` | Patch status | status-controller |

## /storage — 7 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/storage/stats` | Get blob storage statistic *(deprecated)* | blob-storage-controller |
| GET | `/api/storage/upgrade/v2` |  | blob-storage-upgrade-controller |
| POST | `/api/storage/upgrade/v2/test-case-attachment` |  | blob-storage-upgrade-controller |
| POST | `/api/storage/upgrade/v2/test-fixture-result` |  | blob-storage-upgrade-controller |
| POST | `/api/storage/upgrade/v2/test-fixture-result-attachment` |  | blob-storage-upgrade-controller |
| POST | `/api/storage/upgrade/v2/test-result` |  | blob-storage-upgrade-controller |
| POST | `/api/storage/upgrade/v2/test-result-attachment` |  | blob-storage-upgrade-controller |

## /tag — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/tag` | Find all test tags | test-tag-controller |
| POST | `/api/tag` | Create a new test tag | test-tag-controller |
| GET | `/api/tag/suggest` | Suggest test tags | test-tag-controller |
| DELETE | `/api/tag/{id}` | Delete test tag by id | test-tag-controller |
| GET | `/api/tag/{id}` | Find test tag by id | test-tag-controller |
| PATCH | `/api/tag/{id}` | Patch test tag | test-tag-controller |

## /testcase — 101 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testcase` | Find all test cases for specified project | test-case-controller |
| POST | `/api/testcase` | Create a new test case | test-case-controller |
| GET | `/api/testcase/__search` | Find all test cases by given AQL | test-case-search-controller |
| GET | `/api/testcase/attachment` | Find attachments for test case | test-case-attachment-controller |
| POST | `/api/testcase/attachment` | Upload new test case attachments | test-case-attachment-controller |
| DELETE | `/api/testcase/attachment/{id}` | Delete test case attachment | test-case-attachment-controller |
| PATCH | `/api/testcase/attachment/{id}` | Patch test case attachment | test-case-attachment-controller |
| GET | `/api/testcase/attachment/{id}/content` | Get attachment content by id | test-case-attachment-controller |
| PUT | `/api/testcase/attachment/{id}/content` | Update test case attachment content | test-case-attachment-controller |
| GET | `/api/testcase/audit` | Find audit log for test case | test-case-audit-controller |
| POST | `/api/testcase/bulk/cfv/add` | Add custom field values for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/cfv/remove` | Remove custom field values for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/clone` | Clone test cases by ids | test-case-bulk-controller |
| POST | `/api/testcase/bulk/externallink/add` | Add external link for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/issue/add` | Add issues for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/issue/remove` | Remove issues for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/layer/set` | Set specified layer for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/member/add` | Add members for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/member/remove` | Remove member for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/move` | Move test cases to other project | test-case-bulk-controller |
| POST | `/api/testcase/bulk/mute/add` | Add mute for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/remove` | Remove test cases by ids | test-case-bulk-controller |
| POST | `/api/testcase/bulk/run` | Run selected test cases in a new launch | test-case-bulk-controller |
| POST | `/api/testcase/bulk/run/distribution-preview` | Get distribution preview per assignee | test-case-bulk-controller |
| POST | `/api/testcase/bulk/run/existing` | Run selected test cases in an existing launch | test-case-bulk-controller |
| POST | `/api/testcase/bulk/run/new` | Run selected test cases in a new launch | test-case-bulk-controller |
| POST | `/api/testcase/bulk/status/set` | Set specified status for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/sync` | Clone test case | test-case-sync-controller |
| POST | `/api/testcase/bulk/tag/add` | Add tags for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/tag/remove` | Remove tags for all test cases | test-case-bulk-controller |
| POST | `/api/testcase/bulk/testplan/create` | Create test plan from selected test cases | test-case-bulk-controller |
| POST | `/api/testcase/cfv` | Find custom fields with values for test cases | test-case-custom-field-controller |
| GET | `/api/testcase/deleted` | Find all deleted test cases for given project | test-case-controller |
| POST | `/api/testcase/example/nwise` |  | test-case-example-controller |
| GET | `/api/testcase/history` | Find run history for test case | test-case-controller |
| POST | `/api/testcase/import/csv/{importRequestId}/info` | Get testcase csv import file and return import info | test-case-csv-import-controller |
| POST | `/api/testcase/import/csv/{importRequestId}/preview` | Preview testcase csv import | test-case-csv-import-controller |
| POST | `/api/testcase/import/csv/{importRequestId}/submit` | Submit testcase csv import | test-case-csv-import-controller |
| GET | `/api/testcase/muted` | Find all muted test cases for given project | test-case-controller |
| GET | `/api/testcase/query/validate` | Find all test cases by given AQL | test-case-search-controller |
| GET | `/api/testcase/snapshot/max-count` | Get maximum snapshot count for project | test-case-snapshot-controller |
| DELETE | `/api/testcase/snapshot/{id}` | Delete snapshot by identifier | test-case-snapshot-controller |
| GET | `/api/testcase/snapshot/{id}` | Get snapshot by identifier | test-case-snapshot-controller |
| PATCH | `/api/testcase/snapshot/{id}` | Update snapshot title and description | test-case-snapshot-controller |
| POST | `/api/testcase/snapshot/{id}/restore` | Restore a test case from snapshot | test-case-snapshot-controller |
| POST | `/api/testcase/step` | Create scenario step | test-case-scenario-controller |
| DELETE | `/api/testcase/step/{id}` | Delete a specified scenario step | test-case-scenario-controller |
| PATCH | `/api/testcase/step/{id}` | Patch a specified scenario step | test-case-scenario-controller |
| POST | `/api/testcase/step/{id}/copy` | Copy scenario step | test-case-scenario-controller |
| POST | `/api/testcase/step/{id}/move` | Move scenario step | test-case-scenario-controller |
| GET | `/api/testcase/suggest` | Find suggest for test case | test-case-controller |
| POST | `/api/testcase/tms/sync` |  | test-case-export-controller |
| POST | `/api/testcase/version/migrate` | Trigger migration of legacy versions to new snapshots | test-case-snapshot-controller |
| DELETE | `/api/testcase/version/{id}` | Delete version by id | test-case-version-controller |
| GET | `/api/testcase/version/{id}` | Returns version row data | test-case-version-controller |
| PATCH | `/api/testcase/version/{id}` | Patch version | test-case-version-controller |
| GET | `/api/testcase/version/{id}/data` | Returns testcase overview data for given version | test-case-version-controller |
| POST | `/api/testcase/version/{id}/restore` | Create version for test case | test-case-version-controller |
| DELETE | `/api/testcase/{id}` | Delete test case by id | test-case-controller |
| GET | `/api/testcase/{id}` | Find test case by id | test-case-controller |
| PATCH | `/api/testcase/{id}` |  | test-case-controller |
| POST | `/api/testcase/{id}/attachautomation` | Attach automation to test case | test-case-controller |
| POST | `/api/testcase/{id}/clone` | Clone test case | test-case-clone-controller |
| GET | `/api/testcase/{id}/defect` |  | test-case-defect-controller |
| POST | `/api/testcase/{id}/detachautomation` | Detach automation from test case | test-case-controller |
| POST | `/api/testcase/{id}/flaky` | Mark test case as flaky and optionally mute (put in quarantine) it | test-case-controller |
| GET | `/api/testcase/{id}/history` | Find run history for test case | test-case-controller |
| POST | `/api/testcase/{id}/migrate` | Migrate scenario for test case | test-case-scenario-controller |
| POST | `/api/testcase/{id}/restore` | Restore test case by id | test-case-controller |
| DELETE | `/api/testcase/{id}/scenario` | Delete scenario for test case | test-case-scenario-controller |
| GET | `/api/testcase/{id}/scenario` | Find scenario for test case *(deprecated)* | test-case-scenario-controller |
| POST | `/api/testcase/{id}/scenario` | Set new type scenario for test case | test-case-scenario-controller |
| GET | `/api/testcase/{id}/scenariofromrun` | Find scenario for test case from last run | test-case-scenario-controller |
| GET | `/api/testcase/{id}/snapshot` | List snapshots for a test case | test-case-snapshot-controller |
| POST | `/api/testcase/{id}/snapshot` | Create snapshot for a test case | test-case-snapshot-controller |
| DELETE | `/api/testcase/{id}/snapshot/oldest` | Delete N oldest snapshots for a test case | test-case-snapshot-controller |
| GET | `/api/testcase/{id}/stats` | Get statistics for test case | test-case-controller |
| GET | `/api/testcase/{id}/step` | Get scenario for test case | test-case-scenario-controller |
| GET | `/api/testcase/{id}/version` | Returns a list of version for test case | test-case-version-controller |
| POST | `/api/testcase/{id}/version` | Create version for test case | test-case-version-controller |
| GET | `/api/testcase/{id}/workflow` | Find workflow for test case | test-case-controller |
| GET | `/api/testcase/{testCaseId}/cfv` | Find custom fields with values for test case | test-case-custom-field-controller |
| PATCH | `/api/testcase/{testCaseId}/cfv` | Update custom field values of test case | test-case-custom-field-controller |
| DELETE | `/api/testcase/{testCaseId}/defect/{defectId}` |  | test-case-defect-controller |
| POST | `/api/testcase/{testCaseId}/defect/{defectId}` |  | test-case-defect-controller |
| GET | `/api/testcase/{testCaseId}/example` |  | test-case-example-controller |
| POST | `/api/testcase/{testCaseId}/example` |  | test-case-example-controller |
| POST | `/api/testcase/{testCaseId}/example/rename-parameter` |  | test-case-example-controller |
| GET | `/api/testcase/{testCaseId}/issue` | Find issues for test case | test-case-issue-controller |
| POST | `/api/testcase/{testCaseId}/issue` | Set issues to test case | test-case-issue-controller |
| GET | `/api/testcase/{testCaseId}/members` | Find user roles for test case | test-case-members-controller |
| POST | `/api/testcase/{testCaseId}/members` | Set user roles for test case | test-case-members-controller |
| GET | `/api/testcase/{testCaseId}/overview` | Get test case overview | test-case-overview-controller |
| GET | `/api/testcase/{testCaseId}/relation` | Find relations for test case | test-case-relation-controller |
| POST | `/api/testcase/{testCaseId}/relation` | Set relations for test case | test-case-relation-controller |
| GET | `/api/testcase/{testCaseId}/requirement` | Find requirements for test case | test-case-requirement-controller |
| POST | `/api/testcase/{testCaseId}/requirement` | Set requirement to test case | test-case-requirement-controller |
| GET | `/api/testcase/{testCaseId}/tag` | Find tags for test case | test-case-tag-controller |
| POST | `/api/testcase/{testCaseId}/tag` | Set test tags for test case | test-case-tag-controller |
| GET | `/api/testcase/{testCaseId}/testkey` | Find test keys for test case | test-case-test-key-controller |
| POST | `/api/testcase/{testCaseId}/testkey` | Set test keys to test case | test-case-test-key-controller |

## /testcasetree — 13 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testcasetree/countleaves` | Count all tree leaves for given path and filter | test-case-tree-controller |
| GET | `/api/testcasetree/entity` |  | test-case-tree-controller |
| GET | `/api/testcasetree/group` | Find tree groups for node (AQL) | test-case-tree-controller |
| POST | `/api/testcasetree/group` | Add a new group (AQL) | test-case-tree-controller |
| POST | `/api/testcasetree/group/rename` | Rename tree group (AQL) | test-case-tree-controller |
| POST | `/api/testcasetree/job` | Get information about jobs that will be used to run selected test cases | test-case-tree-controller |
| GET | `/api/testcasetree/leaf` | Find tree leaves for node (AQL) | test-case-tree-controller |
| POST | `/api/testcasetree/leaf` | Add a new group | test-case-tree-controller |
| POST | `/api/testcasetree/leaf/rename` | Rename tree leaf | test-case-tree-controller |
| GET | `/api/testcasetree/paths` | Find all paths to test case in tree | test-case-tree-controller |
| POST | `/api/testcasetree/runstats` | Get run information | test-case-tree-controller |
| POST | `/api/testcasetree/select` | Count test cases by tree select | test-case-tree-selection-controller |
| GET | `/api/testcasetree/suggest` | Tree groups suggest | test-case-tree-controller |

## /testcaseupdateschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testcaseupdateschema` | Find all test case update schemas for given project | test-case-update-schema-controller |
| POST | `/api/testcaseupdateschema` | Create a new test case update schema | test-case-update-schema-controller |
| DELETE | `/api/testcaseupdateschema/{id}` | Delete test case update schema by id | test-case-update-schema-controller |
| GET | `/api/testcaseupdateschema/{id}` | Find a test case update schemas by id | test-case-update-schema-controller |
| PATCH | `/api/testcaseupdateschema/{id}` | Patch test case update schema | test-case-update-schema-controller |

## /testfixtureresult — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testfixtureresult/attachment` |  | test-fixture-result-attachment-controller |
| POST | `/api/testfixtureresult/attachment` |  | test-fixture-result-attachment-controller |
| DELETE | `/api/testfixtureresult/attachment/{id}` |  | test-fixture-result-attachment-controller |
| PATCH | `/api/testfixtureresult/attachment/{id}` |  | test-fixture-result-attachment-controller |
| GET | `/api/testfixtureresult/attachment/{id}/content` |  | test-fixture-result-attachment-controller |
| PUT | `/api/testfixtureresult/attachment/{id}/content` |  | test-fixture-result-attachment-controller |

## /testkey — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testkey/{id}` | Find test key by id | test-key-controller |

## /testkeyschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testkeyschema` | Find all test key schemas for given project | test-key-schema-controller |
| POST | `/api/testkeyschema` | Create a new test key schema | test-key-schema-controller |
| DELETE | `/api/testkeyschema/{id}` | Delete a test key schema by id | test-key-schema-controller |
| GET | `/api/testkeyschema/{id}` | Find a test key schema by id | test-key-schema-controller |
| PATCH | `/api/testkeyschema/{id}` | Patch a test key schema | test-key-schema-controller |

## /testlayer — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testlayer` |  | test-layer-controller |
| POST | `/api/testlayer` |  | test-layer-controller |
| GET | `/api/testlayer/suggest` |  | test-layer-controller |
| DELETE | `/api/testlayer/{id}` |  | test-layer-controller |
| GET | `/api/testlayer/{id}` |  | test-layer-controller |
| PATCH | `/api/testlayer/{id}` |  | test-layer-controller |

## /testlayerschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testlayerschema` | Find all test layer schemas for given project | test-layer-schema-controller |
| POST | `/api/testlayerschema` | Create a new test layer schema | test-layer-schema-controller |
| DELETE | `/api/testlayerschema/{id}` | Delete test layer schema by id | test-layer-schema-controller |
| GET | `/api/testlayerschema/{id}` | Find test layer schema by id | test-layer-schema-controller |
| PATCH | `/api/testlayerschema/{id}` | Patch test layer schema | test-layer-schema-controller |

## /testplan — 17 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testplan` | Find all test plans for given project | test-plan-controller |
| POST | `/api/testplan` | Create a new test plan | test-plan-controller |
| GET | `/api/testplan/suggest` | Suggest for test plans | test-plan-controller |
| DELETE | `/api/testplan/{id}` | Delete test plan by given id | test-plan-controller |
| GET | `/api/testplan/{id}` | Find test plan by id | test-plan-controller |
| PATCH | `/api/testplan/{id}` | Patch test plan | test-plan-controller |
| POST | `/api/testplan/{id}/assign` | Assign test plan test cases to user | test-plan-controller |
| GET | `/api/testplan/{id}/diff` | Get test plan test cases changes | test-plan-controller |
| GET | `/api/testplan/{id}/job` | Get test plan jobs statistic | test-plan-controller |
| POST | `/api/testplan/{id}/jobparameter` | Configure test plan job parameters | test-plan-controller |
| GET | `/api/testplan/{id}/member` | Get test plan members statistic | test-plan-controller |
| POST | `/api/testplan/{id}/resetjob` | Reset test plan | test-plan-controller |
| POST | `/api/testplan/{id}/run` | Run test plan by given id | test-plan-controller |
| GET | `/api/testplan/{id}/stat` | Get test plan test-cases statistic | test-plan-controller |
| POST | `/api/testplan/{id}/sync` | Sync test plan | test-plan-controller |
| GET | `/api/testplan/{id}/tree/group` | Find tree groups for node | test-plan-controller |
| GET | `/api/testplan/{id}/tree/leaf` | Find tree leafs for node | test-plan-controller |

## /testresult — 58 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testresult` | Finds all test results by given launch | test-result-controller |
| POST | `/api/testresult` | Create a new test result | test-result-controller |
| GET | `/api/testresult/__search` | Find all test results by given AQL | test-result-search-controller |
| GET | `/api/testresult/attachment` |  | test-result-attachment-controller |
| POST | `/api/testresult/attachment` |  | test-result-attachment-controller |
| DELETE | `/api/testresult/attachment/{id}` |  | test-result-attachment-controller |
| PATCH | `/api/testresult/attachment/{id}` |  | test-result-attachment-controller |
| GET | `/api/testresult/attachment/{id}/content` |  | test-result-attachment-controller |
| PUT | `/api/testresult/attachment/{id}/content` |  | test-result-attachment-controller |
| POST | `/api/testresult/bulk/assign` | Assign all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/defect/link` | Link defects for all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/flaky/confirm-rerun` | Trigger rerun for selected flaky candidate test results to confirm flakiness | test-result-bulk-controller |
| POST | `/api/testresult/bulk/flaky/mark` | Mark selected test results test cases as flaky, optionally muting them | test-result-bulk-controller |
| POST | `/api/testresult/bulk/flaky/unmark` | Unmark selected test results test cases as flaky, optionally unmuting them | test-result-bulk-controller |
| POST | `/api/testresult/bulk/hide` | Hide all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/mute` | Mute all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/rerun` | Rerun all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/resolve` | Resolve all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/tag/add` | Add tags for all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/tag/remove` | Remove tags for all selected test results | test-result-bulk-controller |
| POST | `/api/testresult/bulk/unmute` | Unmute all selected test results | test-result-bulk-controller |
| GET | `/api/testresult/defect/match` |  | test-result-defect-controller |
| GET | `/api/testresult/defects` | Find defects by launch id | test-result-controller |
| GET | `/api/testresult/query/validate` | Find all test results by given AQL | test-result-search-controller |
| GET | `/api/testresult/timeline` | Find timeline data | test-result-controller |
| DELETE | `/api/testresult/{id}` | Delete test result by given id | test-result-controller |
| GET | `/api/testresult/{id}` |  | test-result-controller |
| PATCH | `/api/testresult/{id}` | Patches a test result by given id | test-result-controller |
| POST | `/api/testresult/{id}/assign` | Assign test result | test-result-run-controller |
| GET | `/api/testresult/{id}/defect/candidate` |  | test-result-defect-controller |
| GET | `/api/testresult/{id}/defect/similar` |  | test-result-defect-controller |
| GET | `/api/testresult/{id}/execution` | Find all execution for given test result | test-result-controller |
| POST | `/api/testresult/{id}/flaky` | Mark test result as flaky and optionally mute (put in quarantine) it | test-result-controller |
| GET | `/api/testresult/{id}/history` | Find all history for given test result | test-result-controller |
| POST | `/api/testresult/{id}/in-progress` | Set test result in progress | test-result-run-controller |
| POST | `/api/testresult/{id}/mute` | Mute test result | test-result-mute-controller |
| POST | `/api/testresult/{id}/reject-candidate` | Reject flaky candidate mark for test result | test-result-controller |
| POST | `/api/testresult/{id}/resolve` | Resolve test result | test-result-run-controller |
| GET | `/api/testresult/{id}/retries` | Find all retries for given test result | test-result-controller |
| POST | `/api/testresult/{id}/unmute` | Unmute test result | test-result-mute-controller |
| GET | `/api/testresult/{testResultId}/cfv` | Find custom fields with values for test result | test-result-custom-field-controller |
| POST | `/api/testresult/{testResultId}/cfv` | Set custom field values to test result | test-result-custom-field-controller |
| GET | `/api/testresult/{testResultId}/defect` |  | test-result-defect-controller |
| POST | `/api/testresult/{testResultId}/defect` |  | test-result-defect-controller |
| DELETE | `/api/testresult/{testResultId}/defect/{defectId}` |  | test-result-defect-controller |
| POST | `/api/testresult/{testResultId}/defect/{defectId}` |  | test-result-defect-controller |
| GET | `/api/testresult/{testResultId}/evv` | Find environment variables for test result | test-result-env-var-controller |
| GET | `/api/testresult/{testResultId}/fixture` | Find fixtures for test result | test-result-fixture-controller |
| GET | `/api/testresult/{testResultId}/fixture/attachment` | Find fixtures attachments for test result | test-result-fixture-controller |
| GET | `/api/testresult/{testResultId}/issue` | Find issues for test result | test-result-issue-controller |
| POST | `/api/testresult/{testResultId}/issue` | Set issues to test result | test-result-issue-controller |
| GET | `/api/testresult/{testResultId}/members` | Find user roles for test result | test-result-members-controller |
| POST | `/api/testresult/{testResultId}/members` | Set user roles for test result | test-result-members-controller |
| GET | `/api/testresult/{testResultId}/requirement` | Find requirements for test result | test-result-requirement-controller |
| POST | `/api/testresult/{testResultId}/rerun` | Schedule manual rerun for test case | test-result-rerun-controller |
| POST | `/api/testresult/{testResultId}/retry` | Schedule manual rerun for test case | test-result-rerun-controller |
| GET | `/api/testresult/{testResultId}/testkey` | Find test keys for test result | test-result-test-key-controller |
| POST | `/api/testresult/{testResultId}/testkey` | Set test keys to test result | test-result-test-key-controller |

## /testresulttree — 4 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/testresulttree/countleaves` | Count tree leafs for node | test-result-tree-controller |
| GET | `/api/testresulttree/group` | Find tree groups for node | test-result-tree-controller |
| GET | `/api/testresulttree/leaf` | Find tree leafs for node | test-result-tree-controller |
| POST | `/api/testresulttree/select` | Count test cases by tree select | test-result-tree-selection-controller |

## /token — 3 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/token` | Find all user's api tokens | api-token-controller |
| POST | `/api/token` | Create a new api token | api-token-controller |
| DELETE | `/api/token/{id}` | Delete api token by id | api-token-controller |

## /tree — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/tree` |  | tree-controller |
| POST | `/api/tree` |  | tree-controller |
| GET | `/api/tree/suggest` |  | tree-controller |
| DELETE | `/api/tree/{id}` |  | tree-controller |
| GET | `/api/tree/{id}` |  | tree-controller |
| PATCH | `/api/tree/{id}` |  | tree-controller |

## /tree-folder — 14 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/tree-folder/{projectId}` | Get paginated list of root folders and unassigned test cases | tree-folder-controller |
| POST | `/api/tree-folder/{projectId}/drag-and-drop` | Move folder or testcase to new parent or update position | tree-folder-controller |
| POST | `/api/tree-folder/{projectId}/folder` | Create a new folder | tree-folder-controller |
| GET | `/api/tree-folder/{projectId}/folders/{folderId}/test-cases` | Get test cases in folder with pagination and filtering | tree-folder-controller |
| POST | `/api/tree-folder/{projectId}/migrate-from-tree/{treeId}` | Migrate tree structure from custom field tree to folder tree | tree-folder-migration-controller |
| GET | `/api/tree-folder/{projectId}/root-test-cases` | Get test cases in project root pagination and filtering | tree-folder-controller |
| GET | `/api/tree-folder/{projectId}/suggest` | Suggest distinct folder names | tree-folder-controller |
| POST | `/api/tree-folder/{projectId}/test-case` | Create a new testcase | tree-folder-controller |
| GET | `/api/tree-folder/{projectId}/tree` | Get folder tree structure with test case counts (no pagination) | tree-folder-controller |
| DELETE | `/api/tree-folder/{projectId}/{folderId}` | Delete folder and all its descendants | tree-folder-controller |
| PATCH | `/api/tree-folder/{projectId}/{folderId}` | Update folder name and description | tree-folder-controller |
| GET | `/api/tree-folder/{projectId}/{folderId}/content` | Get folder content including subfolders and test cases | tree-folder-controller |
| GET | `/api/tree-folder/{projectId}/{folderId}/description` | Get folder description | tree-folder-controller |
| DELETE | `/api/tree-folder/{projectId}/{folderId}/test-cases/{testCaseId}` | Remove test case from folder | tree-folder-controller |

## /treepath — 4 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/treepath` |  | tree-path-controller |
| POST | `/api/treepath` |  | tree-path-controller |
| GET | `/api/treepath/path` |  | tree-path-controller |
| DELETE | `/api/treepath/{id}` |  | tree-path-controller |

## /update-testcase-duration — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/update-testcase-duration` | Update test case duration based on median of last 14 passed test results | test-case-duration-update-controller |

## /upload — 8 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| POST | `/api/upload` | Upload test results | upload-controller |
| POST | `/api/upload/archive` | Upload archives with test results | upload-controller |
| POST | `/api/upload/file` | Upload files with test results | upload-controller |
| GET | `/api/upload/jobrun` | Get information about job run by id | upload-controller |
| POST | `/api/upload/run` | Notifies about external job run start | upload-controller |
| POST | `/api/upload/session` | Creates test session for manual upload | upload-controller |
| POST | `/api/upload/start` | Notifies about external job run start | upload-controller |
| POST | `/api/upload/stop` | Notifies about external job run stop | upload-controller |

## /user — 1 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/user/suggest` | Get suggest for users | user-controller |

## /v2 — 46 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/v2/launch/{launchId}/test-result/flat` | Get test results as a flat structure | test-result-flat-controller |
| GET | `/api/v2/launch/{launchId}/test-result/tree` | Get full folder tree with aggregated test result statistics | test-result-tree-controller-v-2 |
| GET | `/api/v2/launch/{launchId}/test-result/tree/entity` | Get test results as a tree structure | test-result-tree-controller-v-2 |
| GET | `/api/v2/launch/{launchId}/test-result/tree/folder` | Get test results as a tree structure | test-result-tree-controller-v-2 |
| GET | `/api/v2/launch/{launchId}/test-result/tree/{folderId}/test-results` | Get test results in folder with pagination and filtering | test-result-tree-controller-v-2 |
| GET | `/api/v2/project/{projectId}/test-case/flat` | Get test cases as a flat structure (AQL) | test-case-flat-controller |
| POST | `/api/v2/project/{projectId}/test-case/flat` | Add a new test case | test-case-flat-controller |
| PUT | `/api/v2/project/{projectId}/test-case/{testCaseId}/flat/name` | Rename the test case | test-case-flat-controller |
| POST | `/api/v2/test-case/bulk/cf/delta` | Find missing custom fields | test-case-cf-bulk-controller |
| POST | `/api/v2/test-case/bulk/cfv` | Find custom fields with values for test cases | test-case-cfv-bulk-controller |
| POST | `/api/v2/test-case/bulk/cfv/add` | Add custom field values for selected test cases | test-case-cfv-bulk-controller |
| POST | `/api/v2/test-case/bulk/cfv/remove` | Remove custom field values for selected test cases | test-case-cfv-bulk-controller |
| POST | `/api/v2/test-case/bulk/clone` | Clone test cases | test-case-bulk-controller-v-2 |
| POST | `/api/v2/test-case/bulk/count` | Count test cases | test-case-bulk-controller-v-2 |
| POST | `/api/v2/test-case/bulk/export/csv` | Generate test cases csv report | test-case-export-bulk-controller |
| POST | `/api/v2/test-case/bulk/export/pdf` | Generate test cases pdf report | test-case-export-bulk-controller |
| POST | `/api/v2/test-case/bulk/external-link/add` | Add external link for selected test cases | test-case-external-link-bulk-controller |
| POST | `/api/v2/test-case/bulk/flaky/mark` | Mark selected test cases as flaky (folder tree selection), optionally muting them | test-case-flaky-bulk-controller |
| POST | `/api/v2/test-case/bulk/flaky/tree/mark` | Mark selected test cases as flaky (group-by tree selection), optionally muting them | test-case-flaky-bulk-controller |
| POST | `/api/v2/test-case/bulk/flaky/tree/unmark` | Unmark selected test cases as flaky (group-by tree selection), optionally unmuting them | test-case-flaky-bulk-controller |
| POST | `/api/v2/test-case/bulk/flaky/unmark` | Unmark selected test cases as flaky (folder tree selection), optionally unmuting them | test-case-flaky-bulk-controller |
| POST | `/api/v2/test-case/bulk/issue/add` | Add issues for selected test cases | test-case-issue-bulk-controller |
| POST | `/api/v2/test-case/bulk/issue/remove` | Remove issues for selected test cases | test-case-issue-bulk-controller |
| POST | `/api/v2/test-case/bulk/job/stats` | Get run information | test-case-run-bulk-controller |
| POST | `/api/v2/test-case/bulk/layer/set` | Set specified layer for selected test cases | test-case-layer-bulk-controller |
| POST | `/api/v2/test-case/bulk/member/add` | Add members for selected test cases | test-case-member-bulk-controller |
| POST | `/api/v2/test-case/bulk/member/remove` | Remove members for selected test cases | test-case-member-bulk-controller |
| POST | `/api/v2/test-case/bulk/move` | Move test cases to another project | test-case-bulk-controller-v-2 |
| POST | `/api/v2/test-case/bulk/mute/add` | Add mute for selected test cases | test-case-mute-bulk-controller |
| POST | `/api/v2/test-case/bulk/remove` | Remove test cases | test-case-bulk-controller-v-2 |
| POST | `/api/v2/test-case/bulk/restore` | Restore test cases | test-case-bulk-controller-v-2 |
| POST | `/api/v2/test-case/bulk/run` | Run selected test cases in a new launch | test-case-run-bulk-controller |
| POST | `/api/v2/test-case/bulk/run/distribution-preview` | Get distribution preview per assignee | test-case-run-bulk-controller |
| POST | `/api/v2/test-case/bulk/run/existing` | Run selected test cases in the existing launch | test-case-run-bulk-controller |
| POST | `/api/v2/test-case/bulk/run/new` | Run selected test cases in a new launch | test-case-run-bulk-controller |
| POST | `/api/v2/test-case/bulk/run/stats` | Get run information | test-case-run-bulk-controller |
| POST | `/api/v2/test-case/bulk/status/set` | Set specified status for selected test cases | test-case-status-bulk-controller |
| POST | `/api/v2/test-case/bulk/tag/add` | Add tags for selected test cases | test-case-tag-bulk-controller |
| POST | `/api/v2/test-case/bulk/tag/remove` | Remove tags for selected test cases | test-case-tag-bulk-controller |
| POST | `/api/v2/test-case/bulk/test-plan/create` | Create test plan from selected test cases | test-case-test-plan-bulk-controller |
| POST | `/api/v2/test-result/bulk/resolve` | Resolve selected test results | test-result-status-bulk-controller |
| POST | `/api/v2/test-result/bulk/run/current-distribution` | Get current distribution per assignee for selected test results | test-result-run-bulk-controller |
| POST | `/api/v2/test-result/bulk/run/distribution-preview` | Get distribution preview per assignee for selected test results | test-result-run-bulk-controller |
| POST | `/api/v2/test-result/bulk/stats` | Get selected test results statistic | test-result-bulk-controller-v-2 |
| GET | `/api/v2/tree` |  | tree-controller-v-2 |
| GET | `/api/v2/tree/{id}` |  | tree-controller-v-2 |

## /widget — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/widget` |  | widget-controller |
| POST | `/api/widget` |  | widget-controller |
| DELETE | `/api/widget/{id}` |  | widget-controller |
| GET | `/api/widget/{id}` |  | widget-controller |
| PATCH | `/api/widget/{id}` |  | widget-controller |
| GET | `/api/widget/{id}/data` |  | widget-controller |

## /workflow — 6 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/workflow` | Find all workflows | workflow-controller |
| POST | `/api/workflow` | Create a new workflow | workflow-controller |
| GET | `/api/workflow/suggest` | Suggest workflows | workflow-controller |
| DELETE | `/api/workflow/{id}` | Delete workflow by given id | workflow-controller |
| GET | `/api/workflow/{id}` | Find workflow by given id | workflow-controller |
| PATCH | `/api/workflow/{id}` | Patch workflow | workflow-controller |

## /workflowschema — 5 операций

| Метод | Путь | Что делает | Тег |
|---|---|---|---|
| GET | `/api/workflowschema` | Find all workflow schemas for given project | workflow-schema-controller |
| POST | `/api/workflowschema` | Create a new workflow schema | workflow-schema-controller |
| DELETE | `/api/workflowschema/{id}` | Delete workflow schema by given id | workflow-schema-controller |
| GET | `/api/workflowschema/{id}` | Find workflow schema by given id | workflow-schema-controller |
| PATCH | `/api/workflowschema/{id}` | Update workflow schema | workflow-schema-controller |
