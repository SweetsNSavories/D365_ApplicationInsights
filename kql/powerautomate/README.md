# powerautomate/

Cloud flow telemetry. Power Automate emits `requests` / `dependencies` rows tagged with flow id, run id, action name when the maker configures App Insights for the flow.

## Files (top level)

| # | File | What it does |
|---|---|---|
| 01 | [`01-flow-run-failures.kql`](01-flow-run-failures.kql) | Failed flow runs over a window |
| 02 | [`02-flow-trigger-failures.kql`](02-flow-trigger-failures.kql) | Trigger failures (skipped/throttled) |
| 03 | [`03-flow-action-failures.kql`](03-flow-action-failures.kql) | Per-action failure breakdown |
| 04 | [`04-flow-runs-with-direct-link.kql`](04-flow-runs-with-direct-link.kql) | All cloud-flow runs with deep link to `make.powerautomate.com/...runs/<runId>` |
| 05 | [`05-flows-in-use-by-trigger.kql`](05-flows-in-use-by-trigger.kql) | Flow-run counts by `FlowDisplayName` × `TriggerName` (joins `requests` ⨝ `dependencies` Cloud-flow-triggers) |
| 06 | [`06-flow-runs-statuses-summary.kql`](06-flow-runs-statuses-summary.kql) | Per-flow nRun / nSuccess / nFailed reliability leaderboard |
| 07 | [`07-trigger-types-in-use.kql`](07-trigger-types-in-use.kql) | Cloud-flow trigger inventory by name (scheduled / webhook / Dataverse / …) |
| 08 | [`08-flowruns-response-time-gt-10s.kql`](08-flowruns-response-time-gt-10s.kql) | Outlier flow runs over 10 seconds — pair with `04` for direct triage link |
| 09 | [`09-process-actions-by-day.kql`](09-process-actions-by-day.kql) | Daily billable actions across a hand-picked cohort of flow IDs (Process-license tracking) |
| 10 | [`10-list-of-flows.kql`](10-list-of-flows.kql) | Distinct (`FlowDisplayName`, `FlowId`) inventory |
| 11 | [`11-flow-actions-by-day-for-flow.kql`](11-flow-actions-by-day-for-flow.kql) | Daily billable actions for one specific flow (replace `_myFlowId`) |
| 12 | [`12-top10-flows-by-billable-actions.kql`](12-top10-flows-by-billable-actions.kql) | Tenant-wide top-10 billable-action leaderboard (excludes skipped actions) |
| 13 | [`13-top10-flows-by-runs.kql`](13-top10-flows-by-runs.kql) | Tenant-wide top-10 flow-run leaderboard |
| 14 | [`14-flow-response-time-p95-timechart.kql`](14-flow-response-time-p95-timechart.kql) | Per-flow P95 duration timechart, 10-min bins |

## Files ([`timelines/`](timelines/))

| # | File | What it does |
|---|---|---|
| 01 | [`timelines/01-cloudflow-runs-daily-30d.kql`](timelines/01-cloudflow-runs-daily-30d.kql) | Daily cloud-flow run count, 30 days |

## Provenance

- 01–03 → [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) cloud-flow telemetry article.
- 04–07 → [`microsoft/AzureMonitorCommunity`](https://github.com/microsoft/AzureMonitorCommunity) — `Azure Services/Power Platform/Power Automate/Queries/Analytics/`.
- 08–14 → [`SinghAmreek/PowerAutomateTelemetry`](https://github.com/SinghAmreek/PowerAutomateTelemetry) — query pack template.
- `timelines/01` → locally authored.
