# `kql/fno/forms/` — D365 F&SCM form usage & performance

Form-load telemetry: most-opened forms, longest-running forms, per-legal-entity distribution, and form-instance timing trends.

## Telemetry shape

| Surface | Notes |
|---|---|
| `pageViews` | Each form open emits a `pageViews` row. `name` is the form name, `duration` is the open-to-render time |
| `customDimensions` keys | `formName`, `legalEntity`, `tenantId`, `appVersion`, `cloudRoleInstance` |
| Client context | `client_City`, `client_CountryOrRegion`, `user_Id`, `session_Id` |

> F&O is one of three main `pageViews` emitters across Dynamics. To isolate F&O traffic vs Model-Driven App vs Power Pages on a shared App Insights resource, filter by `cloud_RoleName in ("AOSService","Web","BatchService")` or by the F&O-only `customDimensions.formName` key. See [../../_shared/timelines/01-pageviews-daily-30d-by-channel.kql](../../_shared/timelines/01-pageviews-daily-30d-by-channel.kql) for the cross-product split.

## Files

| File | Tile (upstream dashboard) |
|---|---|
| [01-top-20-most-opened-forms.kql](01-top-20-most-opened-forms.kql) | Top 20 most opened forms |
| [02-form-usage-by-longest-average-duration.kql](02-form-usage-by-longest-average-duration.kql) | Form usage by longest average duration |
| [03-form-execution-spread.kql](03-form-execution-spread.kql) | Form execution spread |
| [04-form-execution-by-legal-entity.kql](04-form-execution-by-legal-entity.kql) | Form execution by Legal Entity |
| [05-form-instance-execution-times.kql](05-form-instance-execution-times.kql) | Form instance execution times |
| [06-form-duration-trend.kql](06-form-duration-trend.kql) | Form duration trend |
| [07-form-instance-execution-times-2.kql](07-form-instance-execution-times-2.kql) | Form instance execution times (alt view) |

## Source

Extracted from the upstream Microsoft sample dashboard:
`Dashboards/AzureDataExplorer/Forms/ADE-Dashboard-D365FO-Monitoring-Forms.json` in
[microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) (MIT-licensed).

The Microsoft Learn page [Analyze and monitor telemetry with KQL](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-analyze-telemetry-kql) publishes the same two queries (`01-top-20-most-opened-forms.kql` and `02-form-usage-by-longest-average-duration.kql`) as the canonical "first KQL query" tutorial. The dashboard versions here add `_userId` / `_activityId` / `_formName` pass-through parameters on top of the doc form.
