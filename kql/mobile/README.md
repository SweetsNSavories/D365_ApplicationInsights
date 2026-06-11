# mobile/

Power Apps Mobile **offline sync** telemetry. Surfaced as `dependencies` rows with `name == "Offline.SyncDatabase"` (or similar). Used by Field Service and other mobile-first MDA scenarios.

> Note: MDA in a mobile browser (Safari/Chrome on phone) is **not** here — that's still [`../modeldrivenapp/`](../modeldrivenapp/README.md). This folder is for the native Power Apps Mobile app + offline profile.

## Files

| # | File | What it answers |
|---|---|---|
| 01 | [`01-offline-sync-failures-by-errorcode.kql`](01-offline-sync-failures-by-errorcode.kql) | Sync failures grouped by error code |
| 02 | [`02-avg-records-synced-by-table.kql`](02-avg-records-synced-by-table.kql) | Avg records synced per entity |
| 03 | [`03-avg-sync-duration-by-mode.kql`](03-avg-sync-duration-by-mode.kql) | Avg sync duration by mode (initial/delta) |
| 04 | [`04-sync-details-by-user.kql`](04-sync-details-by-user.kql) | Per-user sync detail |
| 05 | [`05-users-by-device-and-version.kql`](05-users-by-device-and-version.kql) | User × device × app version |
| 06 | [`06-sync-type-distribution.kql`](06-sync-type-distribution.kql) | Pie of `DataSyncMode` (FIRST/DELTA/GRID/FORCED) |
| 07 | [`07-daily-users-offline-sync.kql`](07-daily-users-offline-sync.kql) | DAU baseline — distinct `ProfileId` per day |
| 08 | [`08-p95-sync-duration-by-mode-daily.kql`](08-p95-sync-duration-by-mode-daily.kql) | Daily P95 sync duration per `DataSyncMode` |
| 09 | [`09-daily-sync-success-rate.kql`](09-daily-sync-success-rate.kql) | Daily success-rate % from `ScenarioResult` enum |
| 10 | [`10-network-connectivity-by-geo.kql`](10-network-connectivity-by-geo.kql) | Online/offline counts + warm throughput/latency by state × country |
| 11 | [`11-records-synced-timeline-1min.kql`](11-records-synced-timeline-1min.kql) | Records-synced timeline at 1-min resolution (filterable by user/table/mode) |
| 12 | [`12-foreground-vs-background-by-device.kql`](12-foreground-vs-background-by-device.kql) | `ActiveDuration` vs total `duration` P95 by client type × device |
| 13 | [`13-offline-retrievemultiple-perf-join.kql`](13-offline-retrievemultiple-perf-join.kql) | Per-table P50/P95 offline-filter latency — joins `Offline.SyncDatabase` to `SDKRetrieveMultiple` via trimmed `operation_Id` |
| 14 | [`14-avg-payload-size-by-sync-mode.kql`](14-avg-payload-size-by-sync-mode.kql) | Avg sync payload (KB) by `DataSyncMode` from `eventContext.ResponseSize` |

## Provenance

- 01–05 → [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) mobile offline telemetry article.
- 06–14 → [`microsoft/Dynamics-365-FastTrack-Implementation-Assets`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets) — `Customer Service/Field Service/Analytics/dashboard-Field Service Mobile Offline.json` (the public FastTrack Field Service Mobile Offline dashboard).
