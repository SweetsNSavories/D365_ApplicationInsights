# Dashboard — Model-Driven App (UCI) form performance

> **For:** D365 makers, MDA admins, support engineers triaging "form is slow" / "browser error" calls.
> **Signals:** `pageViews` (form/grid loads), `customEvents` (web-resource instrumentation + Monitor tool), `dependencies` (XHR/fetch from UCI), `exceptions` (browser + iOS UCI), `customMetrics` (web-resource counters)
> **Window:** 30 d trends + 7 d top-N
> **Pivot keys:** `customDimensions.appModule`, `customDimensions.entityName`, `client_Browser` / `client_OS`, `client_City`, `session_Id`
> **Prerequisites:** App Insights instrumentation key configured on the App Module ([UCI client telemetry doc](https://learn.microsoft.com/en-us/power-platform/admin/telemetry-events-model-driven-apps)).

## What this dashboard tells you

Everything the **UCI client** reports — form load duration, browser/OS/geo distribution, slowest entities, cold vs warm renders, web-resource client perf, browser and iOS exceptions, and detailed Monitor-tool exports for deep traces.

> **Channel disambiguator:** every tile here implicitly filters `customDimensions.appModule` is populated. If `customDimensions.PortalId` is populated → that's Power Pages → go to [`../powerpages/DASHBOARD-portal-perf.md`](../powerpages/DASHBOARD-portal-perf.md). See [`../_shared/timelines/01-pageviews-daily-30d-by-channel.kql`](../_shared/timelines/01-pageviews-daily-30d-by-channel.kql) for the canonical split.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `[userId]` | 03, 06, 09, 23 | `'00aa…-…-…'` | An Entra user object ID |
| `[sessionIdHere]` | 07, 09 | (Monitor tool ID) | Power Apps Monitor activity / session ID |
| `[Plugin name here]` | n/a | — | (Dataverse-only — not used here) |
| `appModule` | several | `'CaseManagement'` | Filter to a specific app module |
| `ago(7d)` / `ago(30d)` | every tile | `ago(30d)` | Override per tile |

## Tile catalog — top level (`./`)

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Single `pageViews` sample | table | [`01-pageviews-take1.kql`](01-pageviews-take1.kql) | Schema look — what fields/customDimensions are populated |
| 02 | UCI session XHR `dependencies` | table | [`02-uci-request-dependencies.kql`](02-uci-request-dependencies.kql) | Every XHR/fetch a UCI session made |
| 03 | UCI page latency by user | table | [`03-uci-latency-by-user.kql`](03-uci-latency-by-user.kql) | Per-user pageview duration distribution |
| 04 | pageViews by browser/UA | barchart | [`04-useragent-pageviews.kql`](04-useragent-pageviews.kql) | Browser version share |
| 05 | Count by `hostType` | piechart | [`05-hosttype-count.kql`](05-hosttype-count.kql) | Web / Outlook / Mobile App share |
| 06 | `hostType` per user | table | [`06-hosttype-by-user.kql`](06-hosttype-by-user.kql) | Which users use which host |
| 07 | Per-session UCI activity timeline | table | [`07-session-timeline.kql`](07-session-timeline.kql) | All telemetry for one `session_Id` chronologically |
| 08 | Form load duration by geo | barchart | [`08-form-perf-by-location.kql`](08-form-perf-by-location.kql) | Latency × geography |
| 09 | Monitor tool — pull by activity ID | table | [`09-monitor-activity-id.kql`](09-monitor-activity-id.kql) | Drill into a Monitor tool capture |
| 10 | Web-resource `customEvents` parser | table | [`10-customEvents-parse.kql`](10-customEvents-parse.kql) | Parse D365 web-resource `customEvents` payload |
| 11 | Client perf from `customEvents` | table | [`11-customEvents-client-perf.kql`](11-customEvents-client-perf.kql) | Web-resource emitted timings |
| 12 | Browser / device / version info | table | [`12-customEvents-webresource-client-info.kql`](12-customEvents-webresource-client-info.kql) | Client-context fields |
| 13 | UCI on smartphones | timechart | [`13-pageViews-generic-smartphone.kql`](13-pageViews-generic-smartphone.kql) | `Generic Smartphone` UA traffic |
| 14 | Slowest browser/OS combos | barchart | [`14-pageViews-browser-os-slow.kql`](14-pageViews-browser-os-slow.kql) | P95 per (`client_Browser`, `client_OS`) |
| 15 | iOS exceptions | table | [`15-exceptions-ios.kql`](15-exceptions-ios.kql) | UCI on iOS errors |
| 16 | Browser exceptions | table | [`16-exceptions-browser.kql`](16-exceptions-browser.kql) | JS errors caught in UCI |
| 17 | Web-resource request counters | timechart | [`17-customMetrics-webresource-requests.kql`](17-customMetrics-webresource-requests.kql) | `customMetrics`-emitted request counts |
| 18 | Monitor: performance messages | table | [`18-monitor-tool-performance-messages.kql`](18-monitor-tool-performance-messages.kql) | Monitor tool perf-message export |
| 19 | Monitor: req method/code/duration | table | [`19-monitor-tool-requests-method-code-duration.kql`](19-monitor-tool-requests-method-code-duration.kql) | Monitor tool request export |
| 20 | Monitor: resource timings | table | [`20-monitor-tool-requests-resource-timings.kql`](20-monitor-tool-requests-resource-timings.kql) | Browser resource-timing breakdown |
| 21 | Monitor: KPI / FullLoad attribution | table | [`21-monitor-tool-kpi-fullload-attribution.kql`](21-monitor-tool-kpi-fullload-attribution.kql) | Where the form-load wall-time went |
| 22 | Form load cold vs warm by entity | table | [`22-form-load-cold-warm-by-entity.kql`](22-form-load-cold-warm-by-entity.kql) | EditForm cold/warm split with P50/P90/Avg/Max |
| 23 | Network perf per user × country | table | [`23-network-perf-by-user-country.kql`](23-network-perf-by-user-country.kql) | `warmThroughput` min/max/avg by user and country |

## Tile catalog — timelines (`./timelines/`)

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Top 10 slow forms daily P95 (30 d) | timechart | [`timelines/01-mda-top-slow-forms-daily-30d.kql`](timelines/01-mda-top-slow-forms-daily-30d.kql) | Which 10 forms are slowest, each day |

## Flagship tile — paste & run

### Tile 22 · Form load cold vs warm by entity

**Viz:** table
**Source:** [`./22-form-load-cold-warm-by-entity.kql`](./22-form-load-cold-warm-by-entity.kql)

The single most useful tile for "form is slow" calls. EditForm loads are split into **cold** (first load in session — no cache) vs **warm** (subsequent loads), with P50/P90/Avg/Max per entity. A high cold-warm gap on one entity = caching / metadata problem; uniformly slow = server-side.

### Tile 08 · Form load duration by geo

**Viz:** barchart
**Source:** [`./08-form-perf-by-location.kql`](./08-form-perf-by-location.kql)

When the symptom is "only some users are slow", start here. Pair with **23** (network perf per user × country) to confirm whether it's the user's network, not the server.

### Tile timelines/01 · Top 10 slow forms daily P95 (30 d)

**Viz:** timechart
**Source:** [`./timelines/01-mda-top-slow-forms-daily-30d.kql`](./timelines/01-mda-top-slow-forms-daily-30d.kql)

The "did something regress?" question for forms. A jump on a specific day usually corresponds to a release or solution import — pair with [`../dataverse/timelines/07-top10-operations-p95-timeline-30d.kql`](../dataverse/timelines/07-top10-operations-p95-timeline-30d.kql) to see if server-side endpoints jumped at the same time.

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `MDA UCI form performance`.
2. Add your App Insights resource as a data source.
3. Three pages:
   - **Form health** — 14, 22, timelines/01, plus 04/05 for browser/host context
   - **User & geo** — 03, 06, 08, 13, 23
   - **Deep traces (Monitor tool)** — 09, 18, 19, 20, 21
4. Add `_startTime`, `_endTime`, `appModule`, optional `_userId` as dashboard parameters.
5. Save.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-uci-form-perf.md`](./DASHBOARD-uci-form-perf.md). Regenerate the **Form health** page (14, 22, timelines/01, 04, 05) in my App Insights — cluster URI `<...>`, database `<...>`. Filter by appModule `<CaseManagement>`."*

Symptom-driven:

> *"@workspace User '<email>' says the Incident form has been slow since Tuesday. Use this dashboard — start with 03 to confirm, then 22 to split cold/warm, then timelines/01 to see if the regression is broader, then 09 if I supply a Monitor tool activityId."*

## Related dashboards

- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — channel split (MDA vs Portal vs F&O)
- [`../dataverse/DASHBOARD-plugin-and-webapi-health.md`](../dataverse/DASHBOARD-plugin-and-webapi-health.md) — when client-side is fine but `dependencies` from the form are slow, drill server
- [`../powerpages/DASHBOARD-portal-perf.md`](../powerpages/DASHBOARD-portal-perf.md) — same `pageViews` table, different channel
