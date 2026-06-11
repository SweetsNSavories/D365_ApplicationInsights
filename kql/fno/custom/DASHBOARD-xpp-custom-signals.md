# Dashboard — F&O X++ custom telemetry signals

> **For:** F&O developers using `SysApplicationInsightsTelemetryLogger`, ops engineers triaging X++ logon / exception patterns.
> **Signals:** `customEvents`, `traces`, `customMetrics`, `exceptions` (X++ specific via `SysApplicationInsightsTelemetryLogger`)
> **Window:** 1 d hot, 7 d trends
> **Pivot keys:** `customDimensions.UserId`, `customDimensions.ClassName`, `customDimensions.MethodName`, `customDimensions.LegalEntity`, `severityLevel`
> **Prerequisites:** X++ developers calling `SysApplicationInsightsTelemetryLogger` and the relevant `sys.framework` instrumentation switched on in LCS.

## What this dashboard tells you

Six narrow tiles for X++-emitted custom telemetry — what custom signals are flowing at all (inventory), user logon activity, X++ exceptions grouped by class + method, traces by severity, custom-metric breakdown by dimension, and a side-by-side of DMF errors as events versus exceptions.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` / `_endTime` | every tile | `ago(7d)` / `now()` | Default window |
| `_userId` | 02 | `''` (= All) | Pass-through when empty |
| `_legalEntity` | several | `''` (= All) | Pass-through when empty |

## Tile plan

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Custom event inventory | table | [`01-custom-event-inventory.kql`](01-custom-event-inventory.kql) | What custom event names are flowing — the catalog of X++ instrumentation in use |
| 02 | UserLogOn activity | table | [`02-user-logon-activity.kql`](02-user-logon-activity.kql) | Who logged on when, from where |
| 03 | X++ exceptions by class + method | table | [`03-xpp-exceptions-by-class-method.kql`](03-xpp-exceptions-by-class-method.kql) | Exception count grouped by source `ClassName` + `MethodName` |
| 04 | Custom traces by severity | columnchart | [`04-custom-traces-by-severity.kql`](04-custom-traces-by-severity.kql) | Verbose / Information / Warning / Error / Critical share |
| 05 | Custom metrics by dimension | table | [`05-custom-metrics-by-dimension.kql`](05-custom-metrics-by-dimension.kql) | Custom-metric values grouped by dimension key |
| 06 | DMF errors — events vs exceptions | table | [`06-dmf-errors-events-vs-exceptions.kql`](06-dmf-errors-events-vs-exceptions.kql) | Confirms whether DMF errors land in `customEvents` or `exceptions` (depends on the version) |

## Flagship tile — paste & run

### Tile 01 · Custom event inventory

**Viz:** table
**Source:** [`./01-custom-event-inventory.kql`](./01-custom-event-inventory.kql)

The single best starting point when joining a new F&O environment. Tells you what custom instrumentation X++ developers have actually wired up — without this, you may waste time looking for events that simply aren't being emitted.

### Tile 03 · X++ exceptions by class + method

**Viz:** table
**Source:** [`./03-xpp-exceptions-by-class-method.kql`](./03-xpp-exceptions-by-class-method.kql)

The "what's blowing up in X++ land" leaderboard. Source `ClassName` and `MethodName` make this immediately actionable for an X++ developer to open the right object and reproduce.

## Build in Azure Data Explorer dashboards

1. Create dashboard `F&O X++ custom signals`.
2. Add your F&O App Insights resource as a data source.
3. Single page with all 6 tiles is fine.
4. Expose `_startTime`, `_endTime`, `_legalEntity`, `_userId` as dashboard parameters.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-xpp-custom-signals.md`](./DASHBOARD-xpp-custom-signals.md). Build a live dashboard for all 6 tiles in my F&O App Insights — cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace An X++ developer said 'my `Foo.bar()` is throwing intermittently'. Use tile 03 filtered to `ClassName == 'Foo'` and `MethodName == 'bar'` to see counts and recent occurrences, then tile 04 to see if it landed as Error/Critical severity."*

## Related dashboards

- [`../errors/DASHBOARD-errors-triage.md`](../errors/DASHBOARD-errors-triage.md) — broader F&O exception triage (by ExecutionMode / LegalEntity / user)
- [`../dmf/DASHBOARD-dmf-monitoring.md`](../dmf/DASHBOARD-dmf-monitoring.md) — tile 06 cross-references DMF-specific errors
- [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md) — X++ exceptions in batch context appear in both dashboards
