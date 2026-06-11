# modeldrivenapp/

Client-side telemetry for Model-Driven Apps (UCI): `pageViews` (form/grid loads), `customEvents` (web-resource instrumentation), `dependencies` (XHR/fetch from the browser), exceptions from browsers and embedded iOS/Android UCI, plus exports from the Power Apps **Monitor tool**.

## Discriminator

If a `pageViews` row has `customDimensions.appModule` populated → this folder.  
If `customDimensions.PortalId` is populated → see [`../powerpages/`](../powerpages/README.md).  
Otherwise → custom JS SDK / canvas / other.

## Files (top level)

| # | File | What it answers |
|---|---|---|
| 01 | [`01-pageviews-take1.kql`](01-pageviews-take1.kql) | Single `pageViews` row sample |
| 02 | [`02-uci-request-dependencies.kql`](02-uci-request-dependencies.kql) | XHR `dependencies` for a UCI session |
| 03 | [`03-uci-latency-by-user.kql`](03-uci-latency-by-user.kql) | UCI page latency by user |
| 04 | [`04-useragent-pageviews.kql`](04-useragent-pageviews.kql) | `pageViews` grouped by `client_Browser`/UA |
| 05 | [`05-hosttype-count.kql`](05-hosttype-count.kql) | Count by `hostType` (Web, Outlook, etc.) |
| 06 | [`06-hosttype-by-user.kql`](06-hosttype-by-user.kql) | `hostType` per user |
| 07 | [`07-session-timeline.kql`](07-session-timeline.kql) | Per-`session_Id` UCI activity timeline |
| 08 | [`08-form-perf-by-location.kql`](08-form-perf-by-location.kql) | Form load duration by geo |
| 09 | [`09-monitor-activity-id.kql`](09-monitor-activity-id.kql) | Pull everything for a Monitor tool `activityId` |
| 10 | [`10-customEvents-parse.kql`](10-customEvents-parse.kql) | D365 web-resource `customEvents` field parser |
| 11 | [`11-customEvents-client-perf.kql`](11-customEvents-client-perf.kql) | Client perf from `customEvents` |
| 12 | [`12-customEvents-webresource-client-info.kql`](12-customEvents-webresource-client-info.kql) | Browser / device / version info |
| 13 | [`13-pageViews-generic-smartphone.kql`](13-pageViews-generic-smartphone.kql) | UCI on smartphones (`Generic Smartphone` UA) |
| 14 | [`14-pageViews-browser-os-slow.kql`](14-pageViews-browser-os-slow.kql) | Slowest browser/OS combos |
| 15 | [`15-exceptions-ios.kql`](15-exceptions-ios.kql) | iOS-side exceptions |
| 16 | [`16-exceptions-browser.kql`](16-exceptions-browser.kql) | Browser exceptions |
| 17 | [`17-customMetrics-webresource-requests.kql`](17-customMetrics-webresource-requests.kql) | Web-resource request counters |
| 18 | [`18-monitor-tool-performance-messages.kql`](18-monitor-tool-performance-messages.kql) | Monitor: performance messages |
| 19 | [`19-monitor-tool-requests-method-code-duration.kql`](19-monitor-tool-requests-method-code-duration.kql) | Monitor: request method/code/duration |
| 20 | [`20-monitor-tool-requests-resource-timings.kql`](20-monitor-tool-requests-resource-timings.kql) | Monitor: resource timing breakdown |
| 21 | [`21-monitor-tool-kpi-fullload-attribution.kql`](21-monitor-tool-kpi-fullload-attribution.kql) | Monitor: KPI / FullLoad attribution |
| 22 | [`22-form-load-cold-warm-by-entity.kql`](22-form-load-cold-warm-by-entity.kql) | EditForm load times per entity, split cold (first load) vs warm — counts + P50/P90/Avg/Max |
| 23 | [`23-network-perf-by-user-country.kql`](23-network-perf-by-user-country.kql) | Per-user × country `warmThroughput` min/max/avg from `pageViews` |

## Files ([`timelines/`](timelines/))

| # | File |
|---|---|
| 01 | [`timelines/01-mda-top-slow-forms-daily-30d.kql`](timelines/01-mda-top-slow-forms-daily-30d.kql) — top 10 slowest MDA forms, daily P95, 30 days |

## Provenance

- 01–09 → [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) Model-Driven telemetry article.
- 10–17 → [`aliyoussefi/D365-Monitoring`](https://github.com/aliyoussefi/D365-Monitoring).
- 18–21 → [`aliyoussefi/MonitoringPowerPlatform`](https://github.com/aliyoussefi/MonitoringPowerPlatform) Monitor-tool exports.
- 22–23 → [`microsoft/Dynamics-365-FastTrack-Implementation-Assets`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets) — `Customer Service/Customer Service/ComponentLibrary/AppInsights-Telemetry/Dataverse/dashboard-CSAppInsights.json` (also at [Microsoft Learn — Use Application Insights with Dataverse](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/cs-dataverse-appinsights)).
- `timelines/01` → locally authored.
