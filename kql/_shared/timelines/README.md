# _shared/timelines/

Time-series queries that span multiple components — e.g. `pageViews` split by channel (MDA vs Power Pages vs Other), or all-tables pulse counters.

## Files

| # | File | What it does |
|---|---|---|
| 01 | [`01-pageviews-daily-30d-by-channel.kql`](01-pageviews-daily-30d-by-channel.kql) | Daily `pageViews` 30 d, **split by channel** (MDA / Portal / Other) |
| 02 | [`02-pageviews-hourly-7d-by-channel.kql`](02-pageviews-hourly-7d-by-channel.kql) | Hourly `pageViews` 7 d, by channel |
| 03 | [`03-pageviews-duration-percentiles-30d.kql`](03-pageviews-duration-percentiles-30d.kql) | Page-load duration P50/P95 by channel, 30 d |
| 04 | [`04-pageviews-dau-30d-by-channel.kql`](04-pageviews-dau-30d-by-channel.kql) | Daily Active Users by channel, 30 d |
| 05 | [`05-exceptions-daily-30d-top-problems.kql`](05-exceptions-daily-30d-top-problems.kql) | Top exception messages, daily, 30 d (apply noise filter from `_shared/exceptions/02-known-noise-filter.kql` first) |
| 06 | [`06-all-tables-pulse-24h.kql`](06-all-tables-pulse-24h.kql) | `union *` row count per table, last 24 h — is anything dark? |
| 07 | [`07-all-tables-weekly-90d.kql`](07-all-tables-weekly-90d.kql) | `union *` weekly volume per table, 90 d — long-term trend |

## Channel discriminator

```kql
let _ch = (cd:dynamic) {
    case(
        isnotempty(tostring(cd.PortalId)),     "PowerPages",
        isnotempty(tostring(cd.appModule)),    "ModelDrivenApp",
        "Other"
    )
};
pageViews
| extend channel = _ch(parse_json(customDimensions))
```
