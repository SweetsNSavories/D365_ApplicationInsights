# Dashboard — Field Service Mobile (offline-sync analytics)

> **For:** Dynamics 365 Field Service admins, mobile-offline owners, FSCM frontline-worker support.
> **Signals:** `dependencies` (`name == "Offline.SyncDatabase"`, `name startswith "Offline.DataSyncV3"`, `name startswith "Offline.DdsClient"`), `pageViews` (`hostType == "MobileApplication"` for network telemetry), `exceptions`
> **Window:** parameterised — `_startTime` / `_endTime` (defaults 30 d / now)
> **Pivot keys:** `customDimensions.DataSyncMode` (`FIRST_SYNC` / `DELTA_SYNC` / `GRID_REFRESH` / `FORCED_SYNC`), `user_Id`, `customDimensions.AppInfo_Version`, `DeviceInfo_OsName`, `DeviceInfo_make` + `DeviceInfo_model`
> **Prerequisites:** Offline + Dataverse telemetry exported to your App Insights ([Field Service Mobile sample dashboard doc](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/field-service-mobile-sample-telemetry), [importable JSON](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets/blob/master/Customer%20Service/Field%20Service/Analytics/dashboard-Field%20Service%20Mobile%20Offline.json)).

## What this dashboard tells you

The full Microsoft Field Service Mobile Offline analytics dashboard, mirrored as paste-and-run KQL files. Five sub-dashboards in one:

1. **Sync summary** — sync types, daily users, app versions, P95 duration, success rate, device types
2. **Sync errors** — error codes + error timeline
3. **Sync performance** — offline filter perf, network connectivity, foreground vs background by device
4. **Sync payload** — records on device, records-synced timeline, payload size
5. **Sync details** — per-user / per-correlation-ID drill

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` | every tile | `ago(30d)` | Default `ago(30d)` |
| `_endTime` | every tile | `now()` | Default `now()` |
| `dataSyncMode` | several | `''` (= All) | `''` means pass-through; set to `'FIRST_SYNC'`/`'DELTA_SYNC'`/`'GRID_REFRESH'`/`'FORCED_SYNC'` |
| `userId` | error / detail tiles | `''` (= All) | Single representative |
| `tableName` | 11 | `'incident'` | Single Dataverse table |
| `externalCorrelationId` | 13 | `''` (= All) | The customer-supplied correlation ID from the Field Service Mobile **About** page |
| `errorMessage` | error timeline | `''` (= All) | Substring filter |

## Sub-dashboard 1 — Sync summary

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 06 | Distribution of sync types | piechart | [`06-sync-type-distribution.kql`](06-sync-type-distribution.kql) | FIRST / DELTA / GRID / FORCED share — usability red flag if FIRST or GRID dominates |
| 07 | Daily users doing offline sync | timechart | [`07-daily-users-offline-sync.kql`](07-daily-users-offline-sync.kql) | DAU of users actually syncing offline (distinct `ProfileId`) |
| 05 | Users by device + app version | table | [`05-users-by-device-and-version.kql`](05-users-by-device-and-version.kql) | Version rollout across Android / iOS / Windows |
| 08 | P95 sync duration by mode (daily) | timechart | [`08-p95-sync-duration-by-mode-daily.kql`](08-p95-sync-duration-by-mode-daily.kql) | Per-mode P95 trend |
| 09 | Daily sync success rate | timechart | [`09-daily-sync-success-rate.kql`](09-daily-sync-success-rate.kql) | `ScenarioResult == "SUCCESS"` / (`SUCCESS` + `FAILURE`) per day |
| (devices) | Device types | piechart | (same as the **Distribution of sync types** in the upstream JSON — derived from `05` by grouping `DeviceInfo_MakeModel`) | Distribution of devices |

## Sub-dashboard 2 — Sync errors

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Failures by error code | table | [`01-offline-sync-failures-by-errorcode.kql`](01-offline-sync-failures-by-errorcode.kql) | Errors grouped by `ErrorCode` × `ErrorMessage` × `FailureType` × day |

> The upstream JSON dashboard's "sync errors summary" and "sync errors timeline" both source from this query — the only differences are aggregation (summary = drop `bin(timestamp, 1d)`) and viz (timeline = `render timechart`).

## Sub-dashboard 3 — Sync performance

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 13 | Offline filter perf (`SDKRetrieveMultiple` join) | table | [`13-offline-retrievemultiple-perf-join.kql`](13-offline-retrievemultiple-perf-join.kql) | P50/P95 server time per Dataverse table joined with the sync's `operation_Id` |
| 10 | Network connectivity by geo | table | [`10-network-connectivity-by-geo.kql`](10-network-connectivity-by-geo.kql) | Online/offline counts + `warmThroughput` / `warmLatency` per state × country |
| 12 | Foreground vs background by device | table | [`12-foreground-vs-background-by-device.kql`](12-foreground-vs-background-by-device.kql) | `ActiveDuration` vs total `duration` P95 by client × device |

## Sub-dashboard 4 — Sync payload

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 02 | Avg records synced by table | piechart | [`02-avg-records-synced-by-table.kql`](02-avg-records-synced-by-table.kql) | Which Dataverse entities dominate sync payload |
| 11 | Records-synced timeline (1-min) | timechart | [`11-records-synced-timeline-1min.kql`](11-records-synced-timeline-1min.kql) | Sub-minute timeline of records flowing per table / mode / user |
| 14 | Avg payload size (KB) by sync mode | barchart | [`14-avg-payload-size-by-sync-mode.kql`](14-avg-payload-size-by-sync-mode.kql) | Average response size per `DataSyncMode` from `eventContext.ResponseSize` |

## Sub-dashboard 5 — Sync details

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 04 | Detailed sync per user | table | [`04-sync-details-by-user.kql`](04-sync-details-by-user.kql) | Per-user / per-external-correlation-ID drill: P95 active / background duration, last error message, sync count, failures |
| 03 | Avg sync duration by mode | barchart | [`03-avg-sync-duration-by-mode.kql`](03-avg-sync-duration-by-mode.kql) | Baseline avg duration per sync mode |

## Flagship tile — paste & run

### Tile 09 · Daily sync success rate

**Viz:** timechart
**Source:** [`./09-daily-sync-success-rate.kql`](./09-daily-sync-success-rate.kql)

```kusto
dependencies
| where timestamp between  (_startTime.._endTime)
| where name endswith "Offline.SyncDatabase"
| extend cd = parse_json(customDimensions)
| extend eventContext = parse_json(tostring(cd.eventContext))
| extend syncMode = tostring(customDimensions.DataSyncMode)
| extend EventName = tostring(cd.eventName)
| extend ScenarioResult = tostring(cd.ScenarioResult)
| where isempty(['dataSyncMode']) or syncMode in (['dataSyncMode'])
| where isnotempty(ScenarioResult)
| summarize Success = todouble(countif(ScenarioResult == "SUCCESS")),
            All     = countif(ScenarioResult == "SUCCESS" or ScenarioResult == "FAILURE")
        by bin(timestamp, 1d)
| extend SuccessRate = todouble(Success/All) * 100
| project timestamp, SuccessRate
```

Headline reliability number. A dip on a specific date usually pairs with a server-side incident (drill to tile 01 for error codes that spiked) or a Dataverse perf regression (cross-reference with [`../dataverse/timelines/02-requests-failure-rate-30d.kql`](../dataverse/timelines/02-requests-failure-rate-30d.kql)).

### Tile 13 · Offline filter perf (`SDKRetrieveMultiple` join)

**Viz:** table
**Source:** [`./13-offline-retrievemultiple-perf-join.kql`](./13-offline-retrievemultiple-perf-join.kql)

The "why is sync slow?" tile. Joins the client-side `Offline.SyncDatabase` rows with their server-side `SDKRetrieveMultiple` dependencies via trimmed `operation_Id`, then ranks tables by P95 server time. A table near the top with high P95 = a candidate for offline-filter pruning or table-column-selection (covered in the [Best Practices for Offline Mode in the Field Service mobile app](https://www.microsoft.com/dynamics-365/blog/administrator/2023/11/06/best-practices-for-offline-mode-in-the-field-service-mobile-app-part-1/) blog series).

## Build in Azure Data Explorer dashboards

This dashboard is shipped as **importable JSON** by Microsoft. The fastest path:

1. Download [`dashboard-Field Service Mobile Offline.json`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets/blob/master/Customer%20Service/Field%20Service/Analytics/dashboard-Field%20Service%20Mobile%20Offline.json) from the FastTrack Implementation Assets repo.
2. Open [Azure Data Explorer dashboards](https://dataexplorer.azure.com/dashboards) → **New dashboard** → **Import file** → pick the JSON.
3. Edit the data source connection — replace the placeholder cluster URI with your App Insights cluster URI (see [`../../GUIDE-USING-WITH-COPILOT.md`](../../GUIDE-USING-WITH-COPILOT.md)).
4. Save.

If you'd rather build from scratch (e.g. to keep dashboard schema in source control):

1. Create dashboard `Field Service Mobile — Offline analytics`.
2. Five pages matching the sub-dashboards above (Sync summary / Sync errors / Sync performance / Sync payload / Sync details).
3. For each tile in the tile plan, **+ Add tile**, paste the linked `.kql`, pick the **Viz** column value.
4. Add `_startTime`, `_endTime`, `dataSyncMode`, `userId`, `tableName`, `externalCorrelationId`, `errorMessage` as dashboard parameters (defaults per the table above).

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-fs-mobile-offline.md`](./DASHBOARD-fs-mobile-offline.md). Build a live dashboard for the **Sync summary** sub-dashboard (tiles 05, 06, 07, 08, 09) in my App Insights resource. Cluster URI `<...>`, database `<...>`. Default time window is 30 days."*

Symptom-driven:

> *"@workspace Field technicians are reporting offline sync is failing intermittently this week. Use this dashboard — start with tile 09 to confirm the success-rate dip, then tile 01 to see which error codes are dominating the failures, then tile 04 to drill into one user with `userId` `<...>`."*

Performance angle:

> *"@workspace 'Sync is slow on iPads'. Use tile 12 (foreground vs background by device) and tile 13 (offline filter perf join) to identify whether it's a device-class problem or a slow Dataverse table."*

## Related dashboards

- [`../dataverse/DASHBOARD-plugin-and-webapi-health.md`](../dataverse/DASHBOARD-plugin-and-webapi-health.md) — tile 13's join lands on the server side; if a table's P95 is high there, it's a Dataverse problem, not a client one
- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — channel split / noise filter context
- [`../resourcegraph/DASHBOARD-tenant-inventory.md`](../resourcegraph/DASHBOARD-tenant-inventory.md) — list of offline profiles isn't in App Insights but their resource counts are in ARG
