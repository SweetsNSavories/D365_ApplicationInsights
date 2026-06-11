# Dashboard — Dataverse plug-in & Web API health

> **For:** Dataverse admins, plug-in developers, integration owners.
> **Signals:** `requests` (Web API), `dependencies` (plug-ins + SDK), `exceptions` (server-side), `customEvents` (RemoteExecutionContext)
> **Window:** 30 d trends + 7 d top-N
> **Pivot keys:** `name` (request path / plug-in step), `customDimensions.pluginType`, `user_AuthenticatedId`, `client_City`
> **Prerequisites:** Dataverse → App Insights integration enabled ([onboarding](https://learn.microsoft.com/en-us/power-platform/admin/overview-integration-application-insights)).

## What this dashboard tells you

The 360° view of your Dataverse server tier — Web API request volume and latency, plug-in execution and regressions, SDK call cost, and server-side exceptions after the standard noise filter.

This is where ~80% of actionable App Insights data lives for any Dataverse-backed environment. Start here when symptoms point at "Save is slow", "I got a 5xx", "the plug-in pipeline is timing out", or "something changed last week".

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `[userId]` | 05, 10, 23 | `'00aaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'` | A Dataverse user GUID |
| `[Plugin name here]` | 02, 14 | `'Contoso.Plugins.UpdateAccount'` | A plug-in type FQN |
| `<x-ms-service-request-id>` | 10 | `'b3b1f1a2-…-…'` | Pull from a failed request header |
| `ago(7d)` / `ago(30d)` | every tile | `ago(30d)` | Override per tile |

## Tile catalog — top level (`./`)

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Top user agents calling Web API | barchart | [`01-requests-by-useragent.kql`](01-requests-by-useragent.kql) | Who/what is hitting the API |
| 02 | Top 100 plug-in executions by latency | table | [`02-plugin-dependencies-top100.kql`](02-plugin-dependencies-top100.kql) | Slowest single plug-in invocations |
| 03 | SDK call breakdown | table | [`03-sdk-dependencies.kql`](03-sdk-dependencies.kql) | What SDK operations dominate `dependencies` |
| 04 | Top 10 exception messages | barchart | [`04-exceptions-top10.kql`](04-exceptions-top10.kql) | Headline exception list |
| 05 | Exceptions per user | table | [`05-exceptions-by-user.kql`](05-exceptions-by-user.kql) | Which users hit the most server errors |
| 06 | `Retrieve` / `RetrieveMultiple` cost | table | [`06-sdk-retrieve-dependencies.kql`](06-sdk-retrieve-dependencies.kql) | Read-heavy callers |
| 07 | Plug-in perf regressions | columnchart | [`07-plugin-perf-degradation.kql`](07-plugin-perf-degradation.kql) | Plug-ins that got slower across a window |
| 08 | API latency timechart | timechart | [`08-api-perf-timechart.kql`](08-api-perf-timechart.kql) | API latency over time |
| 09 | Plug-in usage × performance | scatterchart | [`09-plugin-usage-perf.kql`](09-plugin-usage-perf.kql) | Heavy callers vs slow ones |
| 10 | Pull telemetry for `x-ms-service-request-id` | table | [`10-telemetry-by-request-id.kql`](10-telemetry-by-request-id.kql) | Full walk for one failed request |
| 11 | Parse RemoteExecutionContext | table | [`11-customEvents-remoteExecutionContext.kql`](11-customEvents-remoteExecutionContext.kql) | Inspect plug-in trace `customEvents` payload |
| 12 | Non-web exceptions | table | [`12-exceptions-non-web.kql`](12-exceptions-non-web.kql) | Plug-in / SDK / background errors |
| 13 | Plug-ins with unpredictable tail latency | scatterchart | [`13-top-plugins-pt95-vs-pt50-ratio.kql`](13-top-plugins-pt95-vs-pt50-ratio.kql) | High `P95/P50` ratio — variable, hard-to-rely-on perf |
| 14 | Most-failed plug-ins by `pluginType` | barchart | [`14-most-failed-plugins-by-plugintype.kql`](14-most-failed-plugins-by-plugintype.kql) | Failures grouped by .NET type, not SDK step name |
| 15 | Plug-ins firing at depth > 2 | table | [`15-plugins-depth-gt-2-weekly.kql`](15-plugins-depth-gt-2-weekly.kql) | Nested plug-in chains with high P95 |

## Tile catalog — timelines (`./timelines/`)

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Requests daily (30 d) | timechart | [`timelines/01-requests-daily-30d.kql`](timelines/01-requests-daily-30d.kql) | Daily Web API request count |
| 02 | Request failure rate (30 d) | timechart | [`timelines/02-requests-failure-rate-30d.kql`](timelines/02-requests-failure-rate-30d.kql) | Daily % of 4xx/5xx |
| 03 | Requests by resultCode (30 d) | columnchart (stacked) | [`timelines/03-requests-by-resultcode-30d.kql`](timelines/03-requests-by-resultcode-30d.kql) | Daily breakdown of status codes |
| 04 | Dependencies daily by type (30 d) | timechart | [`timelines/04-dependencies-daily-30d-by-type.kql`](timelines/04-dependencies-daily-30d-by-type.kql) | SDK vs HTTP vs plug-in dep counts |
| 05 | Plug-ins daily (30 d) | timechart | [`timelines/05-plugins-daily-30d.kql`](timelines/05-plugins-daily-30d.kql) | Daily plug-in execution count |
| 06 | Top 10 operations — percentiles (30 d) | table | [`timelines/06-top10-operations-percentiles-table-30d.kql`](timelines/06-top10-operations-percentiles-table-30d.kql) | P50/P90/P95 per request endpoint |
| 07 | Top 10 operations — P95 timeline (30 d) | timechart | [`timelines/07-top10-operations-p95-timeline-30d.kql`](timelines/07-top10-operations-p95-timeline-30d.kql) | Per-endpoint P95 over time |
| 08 | Top 10 entity-SDKop — percentiles (30 d) | table | [`timelines/08-top10-entity-sdkop-percentiles-table-30d.kql`](timelines/08-top10-entity-sdkop-percentiles-table-30d.kql) | P50/P90/P95 per (entity, SDK message) |
| 09 | Top 10 entity-SDKop — P95 timeline (30 d) | timechart | [`timelines/09-top10-entity-sdkop-p95-timeline-30d.kql`](timelines/09-top10-entity-sdkop-p95-timeline-30d.kql) | Same as 08 over time |
| 10 | Top 10 plug-ins — percentiles (30 d) | table | [`timelines/10-top10-plugins-percentiles-table-30d.kql`](timelines/10-top10-plugins-percentiles-table-30d.kql) | P50/P90/P95 per plug-in |
| 11 | Top 10 plug-ins — P95 timeline (30 d) | timechart | [`timelines/11-top10-plugins-p95-timeline-30d.kql`](timelines/11-top10-plugins-p95-timeline-30d.kql) | Per-plug-in P95 over time |
| 12 | Traffic drop anomaly (business hours, 30 d) | table | [`timelines/12-anomaly-traffic-drop-est-business-hours-30d.kql`](timelines/12-anomaly-traffic-drop-est-business-hours-30d.kql) | `series_decompose_anomalies` — when traffic dropped unexpectedly |
| 13 | Traffic spike anomaly (business hours, 30 d) | table | [`timelines/13-anomaly-traffic-spike-est-business-hours-30d.kql`](timelines/13-anomaly-traffic-spike-est-business-hours-30d.kql) | Unexpected traffic spikes |
| 14 | Traffic anomaly chart (30 d) | timechart | [`timelines/14-anomaly-traffic-chart-30d.kql`](timelines/14-anomaly-traffic-chart-30d.kql) | Anomaly-annotated traffic timechart |
| 15 | 4xx spike anomaly (30 d) | table | [`timelines/15-anomaly-4xx-spike-30d.kql`](timelines/15-anomaly-4xx-spike-30d.kql) | Detect 4xx error spikes |
| 16 | 5xx spike anomaly (30 d) | table | [`timelines/16-anomaly-5xx-spike-30d.kql`](timelines/16-anomaly-5xx-spike-30d.kql) | Detect 5xx error spikes |
| 17 | 4xx/5xx chart (30 d) | timechart | [`timelines/17-anomaly-4xx-5xx-chart-30d.kql`](timelines/17-anomaly-4xx-5xx-chart-30d.kql) | Visualize 4xx/5xx trend with anomaly bands |
| 18 | Top 10 error endpoints (7 d) | barchart | [`timelines/18-top10-error-endpoints-7d.kql`](timelines/18-top10-error-endpoints-7d.kql) | Which endpoints generate the most failures |

## Flagship tile — paste & run

### Tile 04 · Top 10 exception messages

**Viz:** barchart
**Source:** [`./04-exceptions-top10.kql`](./04-exceptions-top10.kql)

Run this first when an "errors" call comes in. **Always pair with** the noise filter from [`../_shared/exceptions/02-known-noise-filter.kql`](../_shared/exceptions/02-known-noise-filter.kql) — on a Dataverse environment ~80% of unfiltered exception rows are `PrvRead`/`PrincipalPrivilegeDenied` noise on first-party (`msdyn*`, `adx_*`, `mscrm_*`) entities, and the real top 10 is hidden under that.

### Tile 06 (timelines) · Top 10 operations — percentiles (30 d)

**Viz:** table
**Source:** [`./timelines/06-top10-operations-percentiles-table-30d.kql`](timelines/06-top10-operations-percentiles-table-30d.kql)

This is the canonical "where is the latency coming from" leaderboard. Pair with tile **07** (timeline) for the same data binned per day — if the P95 jumped on a specific date, that's where to start.

## How to (re)generate in Azure Data Explorer dashboards

1. Create a new dashboard `Dataverse plug-in & Web API health`.
2. Add your App Insights resource as a data source (see [`../../GUIDE-USING-WITH-COPILOT.md`](../../GUIDE-USING-WITH-COPILOT.md) for the URI).
3. Group tiles across **three pages**:
   - **Health** — top-level 01, 04, 08 + timelines 01, 02, 03, 17
   - **Plug-ins** — top-level 02, 07, 09, 13, 14, 15 + timelines 05, 10, 11
   - **Anomalies** — timelines 12–16, 18
4. For each tile, **+ Add tile**, paste the linked `.kql`, pick the **Viz** column value.
5. Expose `_startTime` / `_endTime` as dashboard parameters; default to last 30 days.
6. Save.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-plugin-and-webapi-health.md`](./DASHBOARD-plugin-and-webapi-health.md). Regenerate the **Health** page tiles (01, 04, 08, timelines 01/02/03/17) in my App Insights — cluster URI `<...>`, database `<...>`. Apply the noise filter from `../_shared/exceptions/02-known-noise-filter.kql` to tile 04."*

For a hot-path investigation:

> *"@workspace A user just reported '5xx on /api/data/v9.2/accounts'. Use this dashboard — start with timelines/02, then top-level 04 with the noise filter, then top-level 10 with the request id `<id>`."*

## Related dashboards

- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — confirm the issue is on the Dataverse tier before drilling here
- [`../modeldrivenapp/DASHBOARD-uci-form-perf.md`](../modeldrivenapp/DASHBOARD-uci-form-perf.md) — when the symptom is "form is slow" but server `requests` look fine
- [`../powerautomate/DASHBOARD-flow-runs.md`](../powerautomate/DASHBOARD-flow-runs.md) — when the symptom turns out to be a Power Automate flow hitting the Dataverse API hard
