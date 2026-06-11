# canvasapp/

Canvas App telemetry. Exports from `aliyoussefi/MonitoringPowerPlatform`. Canvas apps emit App Insights data when the maker enables the App Insights instrumentation key on the app and calls `Trace()`/connectors.

## Files

| # | File | What it does |
|---|---|---|
| 01 | [`01-ms-app-identifiers.kql`](01-ms-app-identifiers.kql) | Resolve the `ms-appid`, `appName`, environment from a canvas event |
| 02 | [`02-pageViews-by-session.kql`](02-pageViews-by-session.kql) | Canvas `pageViews` grouped by `session_Id` |
| 03 | [`03-slowest-pages-piechart.kql`](03-slowest-pages-piechart.kql) | Slowest canvas screens as a pie chart |
| 04 | [`04-session-timeline-union.kql`](04-session-timeline-union.kql) | `union *` timeline for a single canvas session |

## Provenance

All four → [`aliyoussefi/MonitoringPowerPlatform`](https://github.com/aliyoussefi/MonitoringPowerPlatform).
