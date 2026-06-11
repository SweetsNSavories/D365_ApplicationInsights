# Dashboard — Cross-component overview

> **For:** anyone — start here when you don't yet know which component is misbehaving.
> **Signals:** `pageViews`, `exceptions`, `requests`, `dependencies`, `customEvents`, `traces`, `customMetrics`, `browserTimings`, `availabilityResults`
> **Window:** 24 h pulse + 7–30 d trends
> **Pivot key:** App Insights table + channel (`appModule` / `PortalId` / `cloud_RoleName`)
> **Prerequisites:** any Power Platform component sending telemetry to your App Insights resource ([overview onboarding](https://learn.microsoft.com/en-us/power-platform/admin/overview-integration-application-insights))

## What this dashboard tells you

The first-look pulse on an unfamiliar App Insights resource. **Which tables are filling**, which **channels** (MDA vs Power Pages vs F&O vs Other) own the `pageViews`, what the **exception baseline** looks like once you strip out documented noise, and which tables are driving **ingestion cost**.

Use this dashboard before drilling into a specific component dashboard.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `ago(24h)` / `ago(7d)` / `ago(30d)` | every tile | `ago(7d)` | Default windows; override per tile |
| (none) | most tiles | — | Cross-component overview tiles are parameter-free by design |

## Tile plan

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 1 | All-tables pulse (24 h) | table | [`timelines/06-all-tables-pulse-24h.kql`](timelines/06-all-tables-pulse-24h.kql) | Per-table row counts in last 24 h — sanity check that data is flowing |
| 2 | All-tables weekly (90 d) | timechart | [`timelines/07-all-tables-weekly-90d.kql`](timelines/07-all-tables-weekly-90d.kql) | Weekly per-table volume trend |
| 3 | pageViews daily by channel (30 d) | columnchart (stacked) | [`timelines/01-pageviews-daily-30d-by-channel.kql`](timelines/01-pageviews-daily-30d-by-channel.kql) | MDA vs Power Pages vs Other share of `pageViews` |
| 4 | pageViews hourly by channel (7 d) | timechart | [`timelines/02-pageviews-hourly-7d-by-channel.kql`](timelines/02-pageviews-hourly-7d-by-channel.kql) | Hourly traffic shape per channel |
| 5 | pageViews duration percentiles (30 d) | table | [`timelines/03-pageviews-duration-percentiles-30d.kql`](timelines/03-pageviews-duration-percentiles-30d.kql) | P50/P75/P90/P95/P99 of page load duration |
| 6 | DAU by channel (30 d) | timechart | [`timelines/04-pageviews-dau-30d-by-channel.kql`](timelines/04-pageviews-dau-30d-by-channel.kql) | Daily distinct users per channel |
| 7 | Top pageViews (single sample) | table | [`overview/01-pageviews-top100.kql`](overview/01-pageviews-top100.kql) | First-look list of most recent pageviews |
| 8 | Pull all telemetry for one `operation_Id` | table | [`overview/02-pageviews-by-operation-id.kql`](overview/02-pageviews-by-operation-id.kql) | Walk a single correlated user action across tables |
| 9 | Log Analytics output template | table | [`overview/03-loganalytics-azurediagnostics-output.kql`](overview/03-loganalytics-azurediagnostics-output.kql) | Read App Insights data from a Log Analytics workspace (`App*` prefixes) |
| 10 | Exceptions — daily top problems (30 d) | table | [`timelines/05-exceptions-daily-30d-top-problems.kql`](timelines/05-exceptions-daily-30d-top-problems.kql) | Top exception messages per day after noise filter |
| 11 | Exception noise catalog (7 d) | table | [`exceptions/01-noise-catalog-breakdown-7d.kql`](exceptions/01-noise-catalog-breakdown-7d.kql) | Which exceptions are known baseline noise (`PrvRead` etc.) |
| 12 | The `_IsNoise` lambda | (helper) | [`exceptions/02-known-noise-filter.kql`](exceptions/02-known-noise-filter.kql) | Reusable noise filter inlined into 03–07 below |
| 13 | Top 10 real problems (7 d) | barchart | [`exceptions/03-top10-real-problems-7d.kql`](exceptions/03-top10-real-problems-7d.kql) | Top 10 exceptions **after** noise removal — the actionable list |
| 14 | Exceptions signal vs noise (30 d) | columnchart (stacked) | [`exceptions/04-exceptions-signal-vs-noise-30d.kql`](exceptions/04-exceptions-signal-vs-noise-30d.kql) | What % of your exception bill is documented noise |
| 15 | Noise self-check (7 d) | table | [`exceptions/05-noise-self-check-7d.kql`](exceptions/05-noise-self-check-7d.kql) | Confirm the filter still matches your environment's noise |
| 16 | Noise discovery candidates (7 d) | table | [`exceptions/06-noise-discovery-candidates-7d.kql`](exceptions/06-noise-discovery-candidates-7d.kql) | Repetitive high-volume exceptions worth adding to the noise list |
| 17 | First-party prefix breakdown (7 d) | piechart | [`exceptions/07-firstparty-prefix-breakdown-7d.kql`](exceptions/07-firstparty-prefix-breakdown-7d.kql) | Share of exceptions by `msdyn*` / `adx_*` / `mscrm_*` prefix |
| 18 | Ingestion volume by table (30 d) | columnchart | [`cost/01-ingestion-volume-by-table-30d.kql`](cost/01-ingestion-volume-by-table-30d.kql) | Daily billable GB per table — where your bill is going |
| 19 | Noisiest signals — sampling candidates | table | [`cost/02-noisy-signals-candidates-for-sampling.kql`](cost/02-noisy-signals-candidates-for-sampling.kql) | High-volume custom-event / trace names to consider sampling or dropping |

## Flagship tile — paste & run

### Tile 1 · All-tables pulse (24 h)

**Viz:** table
**Source:** [`./timelines/06-all-tables-pulse-24h.kql`](./timelines/06-all-tables-pulse-24h.kql)

The single fastest way to confirm "is data even flowing, and from which tables?". If a table you expect to see (e.g. `pageViews` for MDA, `traces` for Conversation Diagnostics) is empty here, the issue is **upstream of KQL** — instrumentation isn't sending.

### Tile 3 · pageViews daily by channel (30 d)

**Viz:** stacked column
**Source:** [`./timelines/01-pageviews-daily-30d-by-channel.kql`](./timelines/01-pageviews-daily-30d-by-channel.kql)

This is the canonical disambiguator for shared App Insights resources. `pageViews` is emitted by **MDA**, **Power Pages**, **F&O**, **Canvas**, and any custom JS SDK — without this split a "slow form load" investigation can land in the wrong folder.

## Build in Azure Data Explorer dashboards

1. Open [Azure Data Explorer dashboards](https://dataexplorer.azure.com/dashboards) and create a new dashboard `Cross-component overview`.
2. **Data sources** → add your App Insights resource using the cluster URI:
   ```
   https://ade.applicationinsights.io/subscriptions/<subscriptionId>/resourcegroups/<rg>/providers/microsoft.insights/components/<appInsightsName>
   ```
   Database name is `<appInsightsName>`.
3. For each row in the **Tile plan**, **+ Add tile** → paste the contents of the linked `.kql` → in **Visual** pick the value from the **Viz** column.
4. Group tiles into two pages: *Pulse & channels* (1–9) and *Exceptions & cost* (10–19).
5. Save.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-overview.md`](./DASHBOARD-overview.md) to build a live dashboard for the 19 tiles in my App Insights resource. Cluster URI is `<my-uri>`, database is `<my-db>`. For each tile in the tile plan, run the linked `.kql` via the Kusto extension, render the suggested visual, write observations from returned rows, and flag tiles that return zero rows."*

For symptom-driven walks:

> *"@workspace I just got access to a Dynamics 365 tenant and I don't know what's wrong. Use [`DASHBOARD-overview.md`](./DASHBOARD-overview.md) — run tiles 1, 3, and 13 first and tell me what stands out."*

## Related dashboards

- [`../dataverse/DASHBOARD-plugin-and-webapi-health.md`](../dataverse/DASHBOARD-plugin-and-webapi-health.md) — drill server-side once you've confirmed the issue is on the Dataverse tier
- [`../modeldrivenapp/DASHBOARD-uci-form-perf.md`](../modeldrivenapp/DASHBOARD-uci-form-perf.md) — drill UCI form / browser side
- [`../powerpages/DASHBOARD-portal-perf.md`](../powerpages/DASHBOARD-portal-perf.md) — drill portal pages
- [`../fno/DASHBOARD-…`](../fno/) — drill F&O tier (Batch / DMF / Errors / Forms / Slow SQL / Custom / Commerce)
