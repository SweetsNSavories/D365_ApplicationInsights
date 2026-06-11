# `kql/fno/slowqueries/` — D365 F&SCM slow SQL queries

Slow SQL surfaced by the AOS — top-N by duration, trend over time, breakdown by query type, and geographic distribution of slow callers. Useful for X++ optimization, missing-index work, and noisy-tenant identification.

## Telemetry shape

| Surface | Notes |
|---|---|
| `customEvents` | `name == "SqlSlow"` (or similar — see `00-reference-slowqueries-script.kql` for the upstream author's filter pattern) |
| `customDimensions` keys | `QueryText`, `QueryHash`, `QueryType`, `DurationMs`, `RowsAffected`, `LegalEntity`, `BatchJobId`, `cloud_RoleInstance` (the AOS that issued the SQL) |
| Client context | `client_City`, `client_CountryOrRegion` for geographic correlation |

## Files

| File | Tile / origin |
|---|---|
| [00-reference-slowqueries-script.kql](00-reference-slowqueries-script.kql) | Upstream standalone reference walkthrough (`KustoQueries/SlowQueries.kql`) — run sections individually |
| [01-slow-queries-reported-by-aos-top-100.kql](01-slow-queries-reported-by-aos-top-100.kql) | Slow queries reported by AOS (Top 100) |
| [02-slow-queries-over-time.kql](02-slow-queries-over-time.kql) | Slow queries over time |
| [03-slow-queries-by-query-type.kql](03-slow-queries-by-query-type.kql) | Slow queries by query type |
| [04-slow-queries-by-client-country-city.kql](04-slow-queries-by-client-country-city.kql) | Slow queries by client country / city |
| [05-top-25-slow-queries-by-duration.kql](05-top-25-slow-queries-by-duration.kql) | Top 25 slow queries by duration |

## Source

Extracted from:
- `KustoQueries/SlowQueries.kql` (the reference walkthrough)
- `Dashboards/AzureDataExplorer/SlowQueries/ADE-Dashboard-D365FO-Monitoring-SlowQueries.json` (the dashboard tiles)

both in [microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) (MIT-licensed).
