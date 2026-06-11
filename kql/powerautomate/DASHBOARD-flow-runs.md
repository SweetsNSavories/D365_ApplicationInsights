# Dashboard — Power Automate cloud flow runs

> **For:** flow makers, integration owners, license / cost watchers.
> **Signals:** `requests` (flow runs), `dependencies` (action / trigger calls)
> **Window:** 7 d top-N + 30 d trends
> **Pivot keys:** `FlowDisplayName` / `FlowId`, `TriggerName`, `ActionName`, `resultCode`
> **Prerequisites:** App Insights configured on the flow ([cloud flow telemetry doc](https://learn.microsoft.com/en-us/power-platform/admin/app-insights-cloud-flow)).

## What this dashboard tells you

Run-level health for cloud flows — failure rate by flow, slowest runs, billable-action leaderboards, and a direct-link tile to jump from "the run that failed" to the actual run page in `make.powerautomate.com`.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_myFlowId` | 11 | `'a1b2c3d4-…-…'` | Set in the `let` at the top of the file |
| `_runId` | (deep-link template in 04) | `'08585…-…'` | A specific run for direct-link generation |
| `ago(7d)` / `ago(30d)` | every tile | `ago(7d)` | Override per tile |

## Tile plan — top level (`./`)

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Failed flow runs | table | [`01-flow-run-failures.kql`](01-flow-run-failures.kql) | Recent flow-run failures |
| 02 | Trigger failures | table | [`02-flow-trigger-failures.kql`](02-flow-trigger-failures.kql) | Trigger-side failures (skipped, throttled) |
| 03 | Per-action failures | table | [`03-flow-action-failures.kql`](03-flow-action-failures.kql) | Which action inside a flow is failing |
| 04 | Runs with deep link | table | [`04-flow-runs-with-direct-link.kql`](04-flow-runs-with-direct-link.kql) | All runs with a clickable `make.powerautomate.com/...` link |
| 05 | Flows in use by trigger | table | [`05-flows-in-use-by-trigger.kql`](05-flows-in-use-by-trigger.kql) | `requests` ⨝ `dependencies` to attribute runs to triggers |
| 06 | Per-flow reliability leaderboard | table | [`06-flow-runs-statuses-summary.kql`](06-flow-runs-statuses-summary.kql) | nRun / nSuccess / nFailed per flow |
| 07 | Trigger types in use | piechart | [`07-trigger-types-in-use.kql`](07-trigger-types-in-use.kql) | Scheduled / webhook / Dataverse / manual share |
| 08 | Runs over 10 seconds | table | [`08-flowruns-response-time-gt-10s.kql`](08-flowruns-response-time-gt-10s.kql) | Outlier runs — pair with 04 for direct-link triage |
| 09 | Daily billable actions across cohort | timechart | [`09-process-actions-by-day.kql`](09-process-actions-by-day.kql) | Per-day billable actions for a hand-picked Process-license cohort |
| 10 | Distinct flow inventory | table | [`10-list-of-flows.kql`](10-list-of-flows.kql) | All `(FlowDisplayName, FlowId)` seen in App Insights |
| 11 | Daily billable actions — one flow | timechart | [`11-flow-actions-by-day-for-flow.kql`](11-flow-actions-by-day-for-flow.kql) | Per-day billable actions for one specific flow |
| 12 | Top 10 flows by billable actions | barchart | [`12-top10-flows-by-billable-actions.kql`](12-top10-flows-by-billable-actions.kql) | Tenant-wide leaderboard |
| 13 | Top 10 flows by runs | barchart | [`13-top10-flows-by-runs.kql`](13-top10-flows-by-runs.kql) | Tenant-wide run leaderboard |
| 14 | Per-flow P95 duration timechart | timechart | [`14-flow-response-time-p95-timechart.kql`](14-flow-response-time-p95-timechart.kql) | P95 per flow, 10-min bins |

## Tile plan — timelines (`./timelines/`)

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Daily cloud-flow runs (30 d) | timechart | [`timelines/01-cloudflow-runs-daily-30d.kql`](timelines/01-cloudflow-runs-daily-30d.kql) | Tenant-wide daily run volume |

## Flagship tile — paste & run

### Tile 06 · Per-flow reliability leaderboard

**Viz:** table
**Source:** [`./06-flow-runs-statuses-summary.kql`](./06-flow-runs-statuses-summary.kql)

The single best "where are my problem flows?" view. Failures sorted by count usually highlight an integration that's been broken for a while; sort by failure rate to find flows that fail unreliably.

### Tile 04 · Runs with deep link

**Viz:** table
**Source:** [`./04-flow-runs-with-direct-link.kql`](./04-flow-runs-with-direct-link.kql)

The triage accelerator. Drop this on the same page as 01/03/08; click any row's link to land directly on the run page in `make.powerautomate.com` to read the action history.

### Tile 12 · Top 10 flows by billable actions

**Viz:** barchart
**Source:** [`./12-top10-flows-by-billable-actions.kql`](./12-top10-flows-by-billable-actions.kql)

The license/cost angle. If a single flow dominates billable actions, it's either (a) doing useful work for the org, or (b) running a hidden loop — pair with tile 11 for that flow to see whether the volume is steady or spiking.

## Build in Azure Data Explorer dashboards

1. Create dashboard `Power Automate cloud flow runs`.
2. Add your App Insights resource as a data source.
3. Three pages:
   - **Triage** — 01, 03, 04, 06, 08 + timelines/01
   - **Inventory** — 05, 07, 10
   - **Cost** — 09, 11, 12, 13, 14
4. Add `_startTime`, `_endTime`, `_flowId` (default empty), `_environmentId` as dashboard parameters.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-flow-runs.md`](./DASHBOARD-flow-runs.md). Build a live dashboard for the **Triage** page (01, 03, 04, 06, 08, timelines/01) in my App Insights — cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace Someone said 'our daily reminders flow has been failing'. Use this dashboard — start with 06 to confirm, then 03 to find which action, then 04 to grab a direct link to the bad run."*

Cost angle:

> *"@workspace Procurement asked about our Power Automate spend. Use the **Cost** page tiles to surface top 10 billable-action flows and per-day trend for the top 3."*

## Related dashboards

- [`../dataverse/DASHBOARD-plugin-and-webapi-health.md`](../dataverse/DASHBOARD-plugin-and-webapi-health.md) — flows hammering Dataverse show up there as request spikes
- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — exception trends may also implicate flows triggered on Dataverse events
- [`../resourcegraph/DASHBOARD-tenant-inventory.md`](../resourcegraph/DASHBOARD-tenant-inventory.md) — tenant-wide flow count via Azure Resource Graph (different runtime)
