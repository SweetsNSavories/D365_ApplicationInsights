# Dashboard — F&O exception triage

> **For:** F&O ops engineers, support analysts triaging "I got an error" calls across the platform.
> **Signal:** `exceptions`
> **Window:** 1 d hot, 7–30 d trends
> **Pivot keys:** `customDimensions.ExecutionMode` (`Interactive` / `Batch` / `Service` / `DMF`), `customDimensions.LegalEntity`, `customDimensions.UserId`, `outerMessage`, `cloud_RoleName`
> **Prerequisites:** F&O telemetry export to App Insights with the standard exception pipeline enabled.

## What this dashboard tells you

Six narrow tiles for F&O exception triage — total error count by execution mode, time-binned counts, top distinct messages, error volume by legal entity, error volume by user, and the raw error list.

This is the most-used dashboard in F&O ops when an incident lands. Open it first, find the dominant facet (mode / entity / user), then drill via the more specific batch / DMF / forms / slow-SQL dashboards.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` / `_endTime` | every tile | `ago(7d)` / `now()` | Default window per file |
| `_executionMode` | several | `''` (= All) | `'Interactive'` / `'Batch'` / `'Service'` / `'DMF'` |
| `_legalEntity` | several | `''` (= All) | Pass-through when empty |
| `_userId` | 05 | `''` (= All) | Pass-through when empty |

## Tile catalog

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Sum of errors per execution mode | piechart | [`01-sum-of-errors-per-execution-mode.kql`](01-sum-of-errors-per-execution-mode.kql) | Interactive vs Batch vs DMF vs Service share — first facet to check |
| 02 | Sum of errors by time span | timechart | [`02-sum-of-errors-by-time-span.kql`](02-sum-of-errors-by-time-span.kql) | Error count over time — spike / regression detection |
| 03 | Errors by outer message | table | [`03-errors-by-outer-message.kql`](03-errors-by-outer-message.kql) | Top distinct exception messages |
| 04 | Errors by legal entity | barchart | [`04-errors-by-legal-entity.kql`](04-errors-by-legal-entity.kql) | Which company is bearing the errors |
| 05 | Errors per user | table | [`05-errors-per-user.kql`](05-errors-per-user.kql) | Which users are hitting the most errors |
| 06 | All errors | table | [`06-all-errors.kql`](06-all-errors.kql) | Raw error list with full message + stack snippet |

## Flagship tile — paste & run

### Tile 01 · Sum of errors per execution mode

**Viz:** piechart
**Source:** [`./01-sum-of-errors-per-execution-mode.kql`](./01-sum-of-errors-per-execution-mode.kql)

The single fastest "where do I drill?" answer. A pie slice >70% on `Batch` → jump to [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md). On `DMF` → [`../dmf/DASHBOARD-dmf-monitoring.md`](../dmf/DASHBOARD-dmf-monitoring.md). On `Interactive` → tile 03 (top messages) + the matching feature folder.

### Tile 03 · Errors by outer message

**Viz:** table
**Source:** [`./03-errors-by-outer-message.kql`](./03-errors-by-outer-message.kql)

The headline list. Sort by count desc; the top 5 messages usually represent >80% of error volume. Skim the message text — if you see `SqlDatabaseException` / "deadlock" / "lock timeout" terms, jump to [`../slowqueries/DASHBOARD-slow-sql.md`](../slowqueries/DASHBOARD-slow-sql.md).

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `F&O exception triage`.
2. Add your F&O App Insights resource as a data source.
3. Single page with all 6 tiles is fine.
4. Expose `_startTime`, `_endTime`, `_executionMode`, `_legalEntity`, `_userId` as dashboard parameters.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-errors-triage.md`](./DASHBOARD-errors-triage.md). Regenerate all 6 tiles in my F&O App Insights — cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace Many users are reporting errors since this morning. Use this dashboard — start with tile 02 to confirm the spike, then tile 01 to pick the execution mode, then tile 03 to get the top messages, then tile 04 to see if it's contained to one legal entity, then tile 06 to read a few examples in detail."*

## Related dashboards

- [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md) — drill if tile 01 points at `Batch`
- [`../dmf/DASHBOARD-dmf-monitoring.md`](../dmf/DASHBOARD-dmf-monitoring.md) — drill if tile 01 points at `DMF`
- [`../slowqueries/DASHBOARD-slow-sql.md`](../slowqueries/DASHBOARD-slow-sql.md) — drill if tile 03 messages look SQL-related
- [`../forms/DASHBOARD-form-perf.md`](../forms/DASHBOARD-form-perf.md) — drill if tile 01 points at `Interactive`
- [`../custom/DASHBOARD-xpp-custom-signals.md`](../custom/DASHBOARD-xpp-custom-signals.md) — drill X++-emitted exceptions (tile 03 there)
