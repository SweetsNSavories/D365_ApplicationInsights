# Dynamics 365 / Power Platform · Application Insights — KQL library

A curated, **vendor-neutral** collection of KQL queries for troubleshooting Microsoft Dynamics 365 and Power Platform workloads that send telemetry to **Azure Application Insights**, organized by component.

Covers **Dataverse, Model-Driven Apps, Power Pages, Canvas, Power Automate, Power Apps Mobile, Copilot Studio, and Dynamics 365 Finance & Supply Chain (F&O / FSCM)**.

Every `.kql` file is **standalone** — paste it into the Logs blade of your App Insights resource and run. No project-wide setup required.

Each folder with runnable tiles also includes `LIVE-DASHBOARD.json` and `LIVE-DASHBOARD.ipynb`. Those files run 10-15 selected KQL tiles through the shared live dashboard runner and write local HTML, Markdown, JSON, and CSV outputs for customer-specific observations.

## Folders

| Folder | What it covers | Runtime |
|---|---|---|
| [`dataverse/`](dataverse/README.md) | Dataverse Web API (`requests`), SDK/HTTP `dependencies`, plug-ins, server-side `exceptions` | App Insights |
| [`modeldrivenapp/`](modeldrivenapp/README.md) | Model-Driven Apps — UCI client `pageViews`, form perf, web-resource `customEvents`/`customMetrics`, Monitor tool exports, browser/iOS exceptions | App Insights |
| [`powerpages/`](powerpages/README.md) | Power Pages portal pages, page perf, anonymous vs authenticated | App Insights |
| [`canvasapp/`](canvasapp/README.md) | Canvas app sessions, slowest screens, multi-table session timeline | App Insights |
| [`powerautomate/`](powerautomate/README.md) | Cloud flow run / trigger / action failures and run cadence | App Insights |
| [`mobile/`](mobile/README.md) | Power Apps Mobile — offline-sync `dependencies` (records synced, durations, error codes) | App Insights |
| [`fno/`](fno/README.md) | D365 Finance & Supply Chain (F&O / FSCM) — Batch jobs, DMF imports/exports, errors, forms, slow SQL, X++ custom telemetry, Commerce POS/CSU/CRT | App Insights |
| [`conversationdiagnostics/`](conversationdiagnostics/README.md) | Customer Service / Contact Center unified-routing conversation traces — lifecycle, fallback queues, overflow, CSR rejections, assignment latency, rep state at point in time | App Insights |
| [`platform-traces/`](platform-traces/README.md) | Generic `traces`-table TSG skeleton (any component that emits SDK traces) | App Insights |
| [`_shared/`](_shared/README.md) | Cross-component utilities: exception **noise filter**, `pageViews` by channel split, all-tables pulse, correlation walks, Log Analytics output, **ingestion cost** | App Insights |
| [`resourcegraph/`](resourcegraph/README.md) | Azure Resource Graph inventory over `PowerPlatformResources` — **NOT App Insights** | Azure Resource Graph |

## How to run a query

1. Open the [Azure portal](https://portal.azure.com) → **Application Insights** → your resource → **Logs**.
2. Open the `.kql` you want.
3. Paste it into the query editor.
4. Substitute any placeholders (see below).
5. Pick a time range from the toolbar (most queries set their own with `ago(7d)` / `ago(30d)` — those override the toolbar).

For Azure Resource Graph queries (under [`resourcegraph/`](resourcegraph/README.md)) use **Resource Graph Explorer** instead, or `az graph query -q "<paste>"`.

## Placeholder convention

Anywhere a query needs a value only you know, you'll see one of these styles. Replace the whole token (brackets included):

| Looks like | Means |
|---|---|
| `[userId]`, `[sessionIdHere]`, `[Plugin name here]` | Customer-supplied value |
| `<URLHere>`, `<resourceId>` | Customer-supplied value (alt notation) |
| `00aa00aa-bb11-cc22-dd33-44ee44ee44ee` | Obvious-fake GUID — substitute with a real one |
| `// Replace …` | Inline instruction immediately above the literal to swap |

Time windows (`ago(7d)`, `ago(30d)`, `bin(timestamp, 1d)`) are intentional defaults — adjust freely.

## Provenance map (source → component folder)

| Source repo / doc | Lands in |
|---|---|
| [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) — Dataverse telemetry doc | `dataverse/` 01–10, `dataverse/timelines/` 01–05 |
| [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) — Model-Driven telemetry doc | `modeldrivenapp/` 01–09 |
| [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) — Mobile offline doc | `mobile/` 01–05 |
| [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) — Cloud flow telemetry doc | `powerautomate/` 01–03 |
| [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) — Overview / Get started doc | `_shared/overview/` 01–02 |
| [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) — Inventory ARG samples | `resourcegraph/` |
| [`aliyoussefi/D365-Monitoring`](https://github.com/aliyoussefi/D365-Monitoring) | `modeldrivenapp/` 10–17 + `dataverse/` 11–12 |
| [`aliyoussefi/MonitoringPowerPlatform`](https://github.com/aliyoussefi/MonitoringPowerPlatform) | `canvasapp/` 01–04 + `modeldrivenapp/` 18–21 + `_shared/overview/03` |
| [`microsoft/powerplatform-telemetry`](https://github.com/microsoft/powerplatform-telemetry) | `platform-traces/` |
| [`microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples`](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) | `fno/` (all 5 subfolders) |
| [`microsoft/Dynamics-365-FastTrack-Implementation-Assets`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets) — `Customer Service/.../dashboard-CSAppInsights.json` & `.../dashboard-Field Service Mobile Offline.json` | `dataverse/` 13–15 + `modeldrivenapp/` 22–23 + `mobile/` 06–14 |
| [`microsoft/AzureMonitorCommunity`](https://github.com/microsoft/AzureMonitorCommunity) — Power Automate analytics samples | `powerautomate/` 04–07 |
| [`SinghAmreek/PowerAutomateTelemetry`](https://github.com/SinghAmreek/PowerAutomateTelemetry) — query-pack template | `powerautomate/` 08–14 |
| [`YAD365/d365-commerce-telemetry`](https://github.com/YAD365/d365-commerce-telemetry) — RetailAPILatency sample (Event ID 5009) | `fno/commerce/` 06 |
| [Microsoft Learn — F&O Monitoring & telemetry](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-overview) (signal-shape docs) | `fno/custom/` 01–06, `_shared/cost/` 01–02 |
| [Microsoft Learn — Commerce App Insights + component-events docs](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/commerce-application-insights) (POS/CRT signal shapes, AppSessionID, Event ID 5000) | `fno/commerce/` 01–05 |
| [Microsoft Learn — Use Application Insights with Dataverse](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/cs-dataverse-appinsights) (canonical doc for the FastTrack dashboard queries) | `dataverse/` 13–15 + `modeldrivenapp/` 22–23 |
| [Microsoft Learn — Sample queries and dashboards for conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/conversation-diagnostics-sample-queries) | `conversationdiagnostics/` 01–19 |
| [Microsoft Learn — Analyze and monitor telemetry with KQL (F&O)](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-analyze-telemetry-kql) | cross-reference for `fno/forms/` 01–02 (same KQL as FastTrack dashboard tiles) |
| Locally authored (timelines, anomalies, exception noise) | `_shared/timelines/`, `_shared/exceptions/`, `dataverse/timelines/` 06–18, `modeldrivenapp/timelines/`, `powerpages/timelines/`, `powerautomate/timelines/` |

## File header convention

```kql
// Source: <repo or doc> / <path-on-source>
// (Optional) Original (if rewritten): <inline link or note>
// (query)
```

The `// Source:` line is preserved on every file regardless of how the file moved during reorganization.

## Where to drop new queries

- Single-component query → that component's folder; numeric prefix continues the sequence.
- Time-series version of an existing query → that component's `timelines/` subfolder.
- Query that joins or compares **multiple components** (e.g. portal vs MDA `pageViews`) → `_shared/timelines/`.
- Reusable lambda or noise filter → `_shared/exceptions/` (or a new `_shared/<topic>/`).
- Azure Resource Graph → `resourcegraph/` — separate runtime, do not mix with App Insights queries.

## Tested against

App Insights **classic** schema (`requests`, `dependencies`, `pageViews`, `exceptions`, `customEvents`, `customMetrics`, `browserTimings`, `availabilityResults`, `traces`). Queries also work against Log Analytics workspace-based App Insights resources — but the table names there carry an `App` prefix:

| Classic App Insights | Log Analytics workspace |
|---|---|
| `traces` | `AppTraces` |
| `pageViews` | `AppPageViews` |
| `exceptions` | `AppExceptions` |
| `customEvents` | `AppEvents` |
| `customMetrics` | `AppMetrics` |
| `requests` | `AppRequests` |
| `dependencies` | `AppDependencies` |
| `availabilityResults` | `AppAvailabilityResults` |
| `browserTimings` | `AppBrowserTimings` |

If you're running the query inside an App Insights resource (the **Logs** blade off the AI resource itself), use the classic names as written. If you're running them from a Log Analytics workspace that holds workspace-based App Insights data, swap to the `App*` names. See [Microsoft Learn — Analyze telemetry with KQL · table name mapping](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-analyze-telemetry-kql#how-can-i-query-telemetry-from-log-analytics).
