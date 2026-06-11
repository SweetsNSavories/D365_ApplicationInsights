# `kql/fno/errors/` — D365 F&SCM platform errors

Top-down exception triage for F&O — by execution mode (interactive / batch / DMF / web), by legal entity, by user, and by outer-message pattern.

## Telemetry shape

| Surface | Notes |
|---|---|
| `exceptions` | Primary table. `outerMessage`, `severityLevel`, `cloud_RoleInstance` (AOS), `session_Id`, `user_Id` |
| `customDimensions` keys | `LegalEntity`, `ExecutionMode`, `BatchJobId`, `CallStack` |
| Client context | `client_Type`, `client_City`, `client_CountryOrRegion` |

`ExecutionMode` values commonly seen: `"Interactive"`, `"Batch"`, `"Service"`, `"DMF"`, `"Import"`.

## Files

| File | Tile (upstream dashboard) |
|---|---|
| [01-sum-of-errors-per-execution-mode.kql](01-sum-of-errors-per-execution-mode.kql) | Sum of errors per Execution Mode |
| [02-sum-of-errors-by-time-span.kql](02-sum-of-errors-by-time-span.kql) | Sum of errors by Time Span |
| [03-errors-by-outer-message.kql](03-errors-by-outer-message.kql) | Errors by outer message |
| [04-errors-by-legal-entity.kql](04-errors-by-legal-entity.kql) | Errors by Legal Entity |
| [05-errors-per-user.kql](05-errors-per-user.kql) | Errors per user |
| [06-all-errors.kql](06-all-errors.kql) | All errors |

## Source

Extracted from the upstream Microsoft sample dashboard:
`Dashboards/AzureDataExplorer/Errors/dashboard-D365FO-Monitoring-Errors.json` in
[microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) (MIT-licensed).
