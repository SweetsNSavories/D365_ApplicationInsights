# `kql/fno/custom/` — X++ custom telemetry signals

Queries for the **custom signals** F&O emits via `SysApplicationInsightsTelemetryLogger`
(events / pageViews / exceptions / traces / metrics). Useful for any environment
that has the Monitoring and telemetry feature enabled and either uses the
out-of-the-box `SysApplicationInsightsGlobalTelemetry` (which auto-logs every X++
Infolog error and form open) or has its own X++ instrumentation on top.

These are **not** in the upstream FastTrack dashboards — they are derived from
the documented signal shapes in
[Add custom telemetry signals](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-developer-add-custom-signals)
and
[Available telemetry](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-available-telemetry).

| File | What it shows |
|---|---|
| [`01-custom-event-inventory.kql`](01-custom-event-inventory.kql) | List every `customEvents.name` your env emits, with volume, users, property-keys, and which `cloud_RoleName` produced it. Run this first on a new resource. |
| [`02-user-logon-activity.kql`](02-user-logon-activity.kql) | The documented `'Admin001' / 'UserLogOn'` custom event (from `SysApplicationInsightsGlobalTelemetry`), pivoted by `UserId` / `UserObjectId` with logons, sessions, distinct computers, and `BuildNum`. |
| [`03-xpp-exceptions-by-class-method.kql`](03-xpp-exceptions-by-class-method.kql) | Top X++ failures pivoted by `ClassName` / `MethodName` with `LegalEntity` / `ExecutionMode` facets and a sample callstack — auto-populated by the global exception telemetry. |
| [`04-custom-traces-by-severity.kql`](04-custom-traces-by-severity.kql) | Custom `traces` bucketed by `SeverityLevel` (Verbose / Information / Warning / Error / Critical) as a stacked area, 14 d. Great for catching debug noise that's driving ingest cost. |
| [`05-custom-metrics-by-dimension.kql`](05-custom-metrics-by-dimension.kql) | Pivots a chosen `customMetrics.name` by any dimension key (default `LegalEntity`). Properly handles the pre-aggregated `valueSum` / `itemCount` AOS rollups. |
| [`06-dmf-errors-events-vs-exceptions.kql`](06-dmf-errors-events-vs-exceptions.kql) | Reconciles DMF errors logged to `customEvents` against those that bubbled to `exceptions`, ranked by error code. |

## How these relate to the FastTrack dashboards in sibling folders

| Sibling folder | Pre-built dashboard signals | This folder |
|---|---|---|
| [`../batch/`](../batch/README.md) | `BatchThreadInfo`, `Batch Start / Stop / Throttling / Failure / Queue / Threads` named events | Generic custom-event triage / inventory |
| [`../dmf/`](../dmf/README.md) | `DMFJob Start`, `DMFJob End`, `DMFJob Status` named events | DMF error reconciliation across customEvents + exceptions |
| [`../forms/`](../forms/README.md) | `pageViews` (form opens with `FormName`, `Duration`) | n/a — covered by sibling |
| [`../errors/`](../errors/README.md) | `exceptions` faceted by `ExecutionMode`, `LegalEntity` | X++ exceptions faceted by `ClassName` / `MethodName` / `CallStack` |
| [`../slowqueries/`](../slowqueries/README.md) | AOS-surfaced slow SQL (`SqlQuery`, `Duration`) | n/a |

## Conventions

- Every file uses an `_lookback` `let` at the top — change it once, runs anywhere.
- Property reads use `coalesce(tostring(cd.X), tostring(cd['X']), tostring(cd['x']))`
  where the F&O property casing isn't guaranteed.
- `cloud_RoleName` discriminator: `AOSService` (interactive), `BatchService`, `DIXFService` (DMF), `Web`.
