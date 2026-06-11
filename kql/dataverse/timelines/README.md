# dataverse/timelines/

Time-series and ranking queries for Dataverse. Most are 30-day windows aligned to UTC; the anomaly queries that key on **EST/EDT business hours** explicitly convert with `datetime_utc_to_local(timestamp, 'US/Eastern')`.

## Files

| # | File | What it does |
|---|---|---|
| 01 | [`01-requests-daily-30d.kql`](01-requests-daily-30d.kql) | Daily Web API request count, 30 days |
| 02 | [`02-requests-failure-rate-30d.kql`](02-requests-failure-rate-30d.kql) | Daily failure-rate (`success==false`) |
| 03 | [`03-requests-by-resultcode-30d.kql`](03-requests-by-resultcode-30d.kql) | Stacked daily count by HTTP `resultCode` |
| 04 | [`04-dependencies-daily-30d-by-type.kql`](04-dependencies-daily-30d-by-type.kql) | Daily `dependencies` count by `type` |
| 05 | [`05-plugins-daily-30d.kql`](05-plugins-daily-30d.kql) | Daily plug-in execution count |
| 06 | [`06-top10-operations-percentiles-table-30d.kql`](06-top10-operations-percentiles-table-30d.kql) | Top 10 operations, P50/P75/P90/P95/P99 table |
| 07 | [`07-top10-operations-p95-timeline-30d.kql`](07-top10-operations-p95-timeline-30d.kql) | Top 10 operations, daily P95 timeline |
| 08 | [`08-top10-entity-sdkop-percentiles-table-30d.kql`](08-top10-entity-sdkop-percentiles-table-30d.kql) | Top 10 (entity, SDK op) percentile table |
| 09 | [`09-top10-entity-sdkop-p95-timeline-30d.kql`](09-top10-entity-sdkop-p95-timeline-30d.kql) | Top 10 (entity, SDK op) P95 timeline |
| 10 | [`10-top10-plugins-percentiles-table-30d.kql`](10-top10-plugins-percentiles-table-30d.kql) | Top 10 plug-ins percentile table |
| 11 | [`11-top10-plugins-p95-timeline-30d.kql`](11-top10-plugins-p95-timeline-30d.kql) | Top 10 plug-ins daily P95 timeline |
| 12 | [`12-anomaly-traffic-drop-est-business-hours-30d.kql`](12-anomaly-traffic-drop-est-business-hours-30d.kql) | `series_decompose_anomalies` traffic DROP, ET 9–17 weekdays |
| 13 | [`13-anomaly-traffic-spike-est-business-hours-30d.kql`](13-anomaly-traffic-spike-est-business-hours-30d.kql) | Traffic SPIKE, ET 9–17 weekdays |
| 14 | [`14-anomaly-traffic-chart-30d.kql`](14-anomaly-traffic-chart-30d.kql) | `render anomalychart` of traffic with markers |
| 15 | [`15-anomaly-4xx-spike-30d.kql`](15-anomaly-4xx-spike-30d.kql) | 4xx spike anomalies |
| 16 | [`16-anomaly-5xx-spike-30d.kql`](16-anomaly-5xx-spike-30d.kql) | 5xx spike anomalies |
| 17 | [`17-anomaly-4xx-5xx-chart-30d.kql`](17-anomaly-4xx-5xx-chart-30d.kql) | Combined 4xx/5xx anomaly chart |
| 18 | [`18-top10-error-endpoints-7d.kql`](18-top10-error-endpoints-7d.kql) | Top 10 error endpoints last 7d |

## Anomaly idiom

```kql
let _step = 1h;
requests
| where timestamp > ago(30d)
| make-series s = count() default = 0 on timestamp from ago(30d) to now() step _step
| extend (anomalies, score, baseline) = series_decompose_anomalies(s, 2.5, -1, 'linefit')
| mv-expand timestamp, s, anomalies, score, baseline to typeof(real)
| where anomalies == -1   // -1 = drop, +1 = spike, 0 = both
| extend t_et = datetime_utc_to_local(todatetime(timestamp), 'US/Eastern')
| where dayofweek(t_et) between (1d .. 5d) and hourofday(t_et) between (9 .. 17)
```

The ET filter is applied **after** decomposition so the baseline isn't skewed by weekend/overnight zeros.
