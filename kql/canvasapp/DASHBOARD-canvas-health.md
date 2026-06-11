# Dashboard — Canvas app health

> **For:** Canvas-app makers, low-code app owners.
> **Signals:** `pageViews` (screen navigations), `customEvents` (`Trace()` calls), `dependencies` (connector calls), `exceptions` (client errors)
> **Window:** 7 d
> **Pivot keys:** `ms-appid` / `appName`, `screenName`, `session_Id`
> **Prerequisites:** App Insights instrumentation key configured on the canvas app and the maker calls `Trace()` / standard connectors with telemetry on.

## What this dashboard tells you

The minimal "is the app healthy?" view for canvas apps — which app instance is reporting, which screens are slowest, and a single-session timeline for deep traces.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `<sessionIdHere>` | 04 | `'aaaaaaaa-bbbb-…-eeeeeeeeeeee'` | A canvas session `session_Id` |
| `<ms-appid>` | (filter) | the app's GUID | From the app's URL or `01` results |
| `ago(7d)` | every tile | `ago(7d)` | Override per tile |

## Tile catalog

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Resolve `ms-appid` / `appName` / environment | table | [`01-ms-app-identifiers.kql`](01-ms-app-identifiers.kql) | Identify which canvas app a row came from |
| 02 | `pageViews` grouped by `session_Id` | table | [`02-pageViews-by-session.kql`](02-pageViews-by-session.kql) | Page-navigation count and duration per session |
| 03 | Slowest screens (pie) | piechart | [`03-slowest-pages-piechart.kql`](03-slowest-pages-piechart.kql) | Share of total time per screen — finds the dominant slow screen |
| 04 | `union *` timeline for a single session | table | [`04-session-timeline-union.kql`](04-session-timeline-union.kql) | All telemetry chronologically for one canvas session |

## Flagship tile — paste & run

### Tile 03 · Slowest screens (pie)

**Viz:** piechart
**Source:** [`./03-slowest-pages-piechart.kql`](./03-slowest-pages-piechart.kql)

The fastest "what should I optimize first?" answer. A pie-slice >50% on one screen = one OnVisible / OnStart / hidden gallery is dominating user time.

### Tile 04 · `union *` timeline for a single session

**Viz:** table
**Source:** [`./04-session-timeline-union.kql`](./04-session-timeline-union.kql)

When a user reports a specific bad experience and gives you their session ID (visible in the in-app diagnostic overlay), this query walks every telemetry surface — page navigations, trace calls, connector dependencies, exceptions — in order.

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `Canvas app health`.
2. Add your App Insights resource as a data source.
3. Single page with all 4 tiles is fine.
4. Add `_startTime`, `_endTime`, optional `_msAppId`, `_sessionId` as dashboard parameters.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-canvas-health.md`](./DASHBOARD-canvas-health.md). Regenerate all four tiles in my App Insights resource — cluster URI `<...>`, database `<...>`. Filter to ms-appid `<...>`."*

Symptom-driven:

> *"@workspace A user said the OrderForm app froze when they tapped Submit on screen `OrderReview`. They gave me sessionId `<id>`. Use tile 04 to walk the session and tell me what failed."*

## Related dashboards

- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — canvas apps emit `pageViews` too, but with neither `appModule` nor `PortalId` — visible as "Other" in the channel split
- [`../powerautomate/DASHBOARD-flow-runs.md`](../powerautomate/DASHBOARD-flow-runs.md) — when the canvas app calls Power Automate flows that fail
- [`../dataverse/DASHBOARD-plugin-and-webapi-health.md`](../dataverse/DASHBOARD-plugin-and-webapi-health.md) — when the canvas app's `dependencies` to Dataverse are the slow link
