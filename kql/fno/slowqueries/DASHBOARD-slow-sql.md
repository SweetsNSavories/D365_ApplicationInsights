# Dashboard — F&O slow queries (AOS-surfaced)

> **For:** F&O DBAs, X++ developers tuning data access, ops engineers triaging "everything is slow" calls.
> **Signal:** `customEvents` with `name` indicating AOS slow-query events — emitted when the AOS-side thresholds for long-running SQL are crossed.
> **Window:** 1 d hot, 7 d trends
> **Pivot keys:** `customDimensions.QueryHash`, `customDimensions.QueryText` (truncated), `customDimensions.UserId`, `customDimensions.client_City`, `customDimensions.client_CountryOrRegion`
> **Prerequisites:** F&O telemetry export to App Insights with slow-query events enabled in LCS.

## What this dashboard tells you

The slowest X++/SQL queries the AOS reported in the window — top 100 over the period, longest-by-duration top 25, query-type distribution, time trend, and geographic distribution of the calling clients. Pair with [`../forms/DASHBOARD-form-perf.md`](../forms/DASHBOARD-form-perf.md) when a slow form's queries surface here.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` / `_endTime` | every tile | `ago(7d)` / `now()` | Default window per file |
| `_queryType` | 03 | `''` (= All) | Pass-through when empty |
| `_country` / `_city` | 04 | `''` (= All) | Pass-through when empty |

## Tile plan

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 00 | Reference: slow-queries data-collection script | (reference) | [`00-reference-slowqueries-script.kql`](00-reference-slowqueries-script.kql) | The instrumentation source — not a dashboard tile; explains how `customEvents` are populated |
| 01 | Slow queries reported by AOS — top 100 | table | [`01-slow-queries-reported-by-aos-top-100.kql`](01-slow-queries-reported-by-aos-top-100.kql) | The headline list — 100 slowest distinct queries |
| 02 | Slow queries over time | timechart | [`02-slow-queries-over-time.kql`](02-slow-queries-over-time.kql) | Slow-query count timeline — regression signal |
| 03 | Slow queries by query type | piechart | [`03-slow-queries-by-query-type.kql`](03-slow-queries-by-query-type.kql) | SELECT / UPDATE / DELETE / etc. share |
| 04 | Slow queries by client country/city | table | [`04-slow-queries-by-client-country-city.kql`](04-slow-queries-by-client-country-city.kql) | Geographic distribution of clients submitting slow queries |
| 05 | Top 25 slow queries by duration | barchart | [`05-top-25-slow-queries-by-duration.kql`](05-top-25-slow-queries-by-duration.kql) | 25 slowest single-execution queries (max duration per query) |

## Flagship tile — paste & run

### Tile 02 · Slow queries over time

**Viz:** timechart
**Source:** [`./02-slow-queries-over-time.kql`](./02-slow-queries-over-time.kql)

The "did something regress?" view. A sudden step-up usually corresponds to (a) a release that introduced a missing index, (b) a parameter-sniffing change after stats refresh, or (c) a data-volume jump on a table. Pair with tile 01 to see which queries showed up on the day of the step-up.

### Tile 01 · Slow queries reported by AOS — top 100

**Viz:** table
**Source:** [`./01-slow-queries-reported-by-aos-top-100.kql`](./01-slow-queries-reported-by-aos-top-100.kql)

The actionable list. Sort by count first (frequent + slow = highest ROI to fix), then by max duration (rare + extremely slow = often deadlock / locking).

## Build in Azure Data Explorer dashboards

1. Create dashboard `F&O slow queries`.
2. Add your F&O App Insights resource as a data source.
3. Single page with the 5 dashboard tiles (skip tile 00 — that's a reference / instrumentation note, not a tile).
4. Expose `_startTime`, `_endTime`, `_queryType`, `_country`, `_city` as dashboard parameters.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-slow-sql.md`](./DASHBOARD-slow-sql.md). Build a live dashboard for tiles 01-05 in my F&O App Insights — cluster URI `<...>`, database `<...>`. Skip tile 00; that's a reference, not a dashboard tile."*

Symptom-driven:

> *"@workspace Users complain that posting is slow. Use this dashboard — tile 02 to confirm a regression today, tile 01 to find the top 5 slow queries since this morning, tile 04 to see if it's geographically concentrated."*

## Related dashboards

- [`../forms/DASHBOARD-form-perf.md`](../forms/DASHBOARD-form-perf.md) — a slow form often has its dominant cost in slow X++ SQL that shows up here
- [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md) — slow SQL inside batch starves threads; cross-reference timeline 02 with batch tile 13 (PBS queue) and tile 05 (available threads)
- [`../errors/DASHBOARD-errors-triage.md`](../errors/DASHBOARD-errors-triage.md) — `SqlDatabaseException` / deadlock messages often co-occur with slow-query spikes
