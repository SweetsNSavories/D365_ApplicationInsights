# `kql/fno/commerce/` — Dynamics 365 Commerce (POS / CSU / CRT)

Telemetry from the Commerce tier of D365 — Commerce Scale Unit (CSU),
Commerce Runtime (CRT), Modern / Cloud POS — sitting on top of the F&O AOS
stack covered by the sibling subfolders.

> Commerce ships with extensible Application Insights instrumentation **on
> both sides** of every POS interaction. The CRT (server-side C# in CSU)
> uses `Microsoft.ApplicationInsights.DataContracts.TraceTelemetry`; Modern
> POS / Cloud POS (client-side TypeScript) uses
> `@microsoft/applicationinsights-web`'s `trackEvent({ name, properties, measurements })`.
> Three correlation IDs flow with every request: **`AppSessionID`** (POS
> startup), **`UserSessionID`** (sign-in), and **`ActivityID`** (one per CSU
> incoming request - logged as **Event ID 5000** on the CSU side).

Sources:
[Log extension events to Application Insights](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/commerce-application-insights) ·
[Commerce component events for diagnostics & troubleshooting](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/retail-component-events-diagnostics-troubleshooting) ·
[Customer orders in POS (async flow)](https://learn.microsoft.com/en-us/dynamics365/commerce/customer-orders-overview) ·
[`YAD365/d365-commerce-telemetry`](https://github.com/YAD365/d365-commerce-telemetry) — RetailAPILatency sample (source of `06`)

## Files

| File | What it shows |
|---|---|
| [`01-pos-extension-events-inventory.kql`](01-pos-extension-events-inventory.kql) | Every `customEvents.name` raised by POS / CRT extensions — counts, users, sessions, roles, `PropertyKeys`, `MeasureKeys`. Run this first to discover what you have. |
| [`02-crt-extension-traces-inventory.kql`](02-crt-extension-traces-inventory.kql) | Server-side CRT extension traces faceted by `CustomDimensionColumn1` (TerminalId) and `CustomDimensionColumn2` (tag), grouped by `SeverityLevel`. |
| [`03-walk-app-session.kql`](03-walk-app-session.kql) | Given one `AppSessionID`, walks `customEvents` + `traces` + `exceptions` + `requests` chronologically. The canonical POS-to-CSU correlation path. |
| [`04-csu-incoming-requests-event-5000.kql`](04-csu-incoming-requests-event-5000.kql) | CSU incoming request health (P50 / P95 / P99 / error %) by `operation_Name` × `resultCode`. Combines the standard `requests` table with a fallback for any custom Event ID 5000 instrumentation. |
| [`05-async-order-processing-batches.kql`](05-async-order-processing-batches.kql) | Daily activity on `RetailDocumentOperationMonitorBatch` / `RetailDocumentOperationProcessingBatch` — the X++ classes the docs name as the async customer-order drivers. |
| [`06-retail-api-latency-event-5009.kql`](06-retail-api-latency-event-5009.kql) | RetailServer API latency P50/P75/P90/P99 binned 5 min, by controller\\action. Uses **Event ID 5009** (`RetailServerRequestFinished`) — distinct from `04`'s Event ID 5000 (`IncomingRequest`). |

> **Event IDs 5000 vs 5009** — 5000 is the *start* envelope for an incoming CSU request (`04`); 5009 is the matching *finished* event that carries the `executionTimeMilliseconds` measurement (`06`). Use 5000 to count traffic and 5009 to measure latency.

## Conventions

- `cloud_RoleName` filters are exposed as `_posRole` / `_csuRole` `let` parameters defaulting to empty string. Empty = pass-through (matches the `isempty(_x) or Column == _x` idiom used everywhere else in the repo). Common observed values: `RetailServer` (CSU), `CloudPOS` / `ModernPOS` (POS clients), `BatchService` (X++ batch runner used by async-order classes).
- Correlation-ID extraction always uses `coalesce(tostring(cd.AppSessionID), tostring(cd.appSessionId), tostring(cd['App Session ID']))` — capitalisation has varied across Commerce releases.
- CRT extension traces are identified by the doc-recommended convention of populating `CustomDimensionColumn1` and `CustomDimensionColumn2`; queries here filter on `isnotempty(...)` of either. Drop that filter to see every trace from the role.

## Related

- [`../batch/`](../batch/README.md) — generic F&O batch framework queries; pairs with `05-async-order-processing-batches.kql`.
- [`../errors/`](../errors/README.md) — broad `exceptions` triage; the AppSession walk in `03` feeds candidates here.
- [`../custom/`](../custom/README.md) — X++ custom telemetry signals (`SysApplicationInsightsTelemetryLogger`) on the headquarters / AOS side.
- [`../../_shared/cost/`](../../_shared/cost/README.md) — POS extensions and CRT traces are common ingestion-cost drivers; check `02-noisy-signals-candidates-for-sampling.kql` if your bill jumps after deploying a Commerce extension.

## Not in scope here

- **Commerce Data Exchange (CDX) sync sessions** — managed in Commerce headquarters, not App Insights. The official troubleshooting flow lives on the Channel database / Download sessions form in HQ; see [CDX troubleshooting](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/cdx-troubleshooting) and [CDX best practices](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/cdx-best-practices). The async-order query in `05` covers the App-Insights-visible piece (the X++ batch classes).
- **LCS Log Search** — a separate Microsoft-hosted indexer (Lifecycle Services → Environment Monitoring → View raw logs). Not queryable via KQL; the docs cover its UI directly.
- **Event Viewer** / browser F12 console — local-only, not part of an App Insights pipeline.
