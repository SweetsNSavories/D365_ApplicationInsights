# dataverse/

Server-side Dataverse telemetry: Web API `requests`, SDK/HTTP `dependencies`, plug-in execution, server-side `exceptions`. This is where 80%+ of the actionable App Insights data sits for a Dataverse-backed environment.

## Files (top level)

| File | What it answers |
|---|---|
| [`01-requests-by-useragent.kql`](01-requests-by-useragent.kql) | Top user agents calling the Web API |
| [`02-plugin-dependencies-top100.kql`](02-plugin-dependencies-top100.kql) | Top 100 plug-in executions by latency |
| [`03-sdk-dependencies.kql`](03-sdk-dependencies.kql) | SDK call breakdown via `dependencies` |
| [`04-exceptions-top10.kql`](04-exceptions-top10.kql) | Top 10 exception messages |
| [`05-exceptions-by-user.kql`](05-exceptions-by-user.kql) | Exception count grouped by user |
| [`06-sdk-retrieve-dependencies.kql`](06-sdk-retrieve-dependencies.kql) | `Retrieve` / `RetrieveMultiple` cost |
| [`07-plugin-perf-degradation.kql`](07-plugin-perf-degradation.kql) | Detect plug-in regressions across a window |
| [`08-api-perf-timechart.kql`](08-api-perf-timechart.kql) | API latency timechart |
| [`09-plugin-usage-perf.kql`](09-plugin-usage-perf.kql) | Plug-in usage × performance correlation |
| [`10-telemetry-by-request-id.kql`](10-telemetry-by-request-id.kql) | All telemetry for a single `x-ms-service-request-id` |
| [`11-customEvents-remoteExecutionContext.kql`](11-customEvents-remoteExecutionContext.kql) | Parse `RemoteExecutionContext` from plug-in trace `customEvents` (D365 Monitoring repo) |
| [`12-exceptions-non-web.kql`](12-exceptions-non-web.kql) | Non-web (plug-in / SDK / background) exceptions (D365 Monitoring repo) |
| [`13-top-plugins-pt95-vs-pt50-ratio.kql`](13-top-plugins-pt95-vs-pt50-ratio.kql) | Custom plug-ins with `AvgExecutionTime > 500 ms` — surfaces `PT95vsPT50Ratio` to spot plug-ins with unpredictable tail latency |
| [`14-most-failed-plugins-by-plugintype.kql`](14-most-failed-plugins-by-plugintype.kql) | Top 10 failed plug-ins attributed by `customDimensions.pluginType` (the .NET type) instead of the SDK step name |
| [`15-plugins-depth-gt-2-weekly.kql`](15-plugins-depth-gt-2-weekly.kql) | Custom plug-ins firing at execution depth > 2 — flags nested plug-in chains with high P95 |

## Files ([`timelines/`](timelines/))

Daily / hourly / anomaly time series — see [`timelines/README.md`](timelines/README.md).

## Notes on noise

Read-privilege exceptions on first-party (`msdyn*`, `adx_*`, `mscrm_*`) entities are baseline noise on every Dataverse-backed environment — use the lambda from [`../_shared/exceptions/02-known-noise-filter.kql`](../_shared/exceptions/02-known-noise-filter.kql) before reporting Dataverse exception trends.

## Provenance

- 01–10 → [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) Dataverse telemetry article (Application Insights → Dataverse).
- 11–12 → [`aliyoussefi/D365-Monitoring`](https://github.com/aliyoussefi/D365-Monitoring).
- 13–15 → [`microsoft/Dynamics-365-FastTrack-Implementation-Assets`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets) — `Customer Service/Customer Service/ComponentLibrary/AppInsights-Telemetry/Dataverse/dashboard-CSAppInsights.json`. Same queries documented at [Microsoft Learn — Use Application Insights with Dataverse](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/cs-dataverse-appinsights).
- `timelines/01–05` → MS Docs derivatives (daily/percentile rollups of 01–10).
- `timelines/06–18` → locally authored top-10 percentile tables, top-10 P95 timelines, `series_decompose_anomalies` drop/spike detection, 4xx/5xx anomaly charts.
