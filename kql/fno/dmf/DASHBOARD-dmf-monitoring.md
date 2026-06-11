# Dashboard — F&O Data Management Framework (DMF) monitoring

> **For:** F&O integration owners, DMF data-project authors, ops engineers triaging "import didn't load" calls.
> **Signals:** `customEvents` (`Event ID 10000` family), `exceptions` (DMF errors), `customMetrics` (record counts, durations)
> **Window:** 1 d hot, 7–30 d trends
> **Pivot keys:** `customDimensions.DataProjectName`, `customDimensions.Entity`, `customDimensions.OperationType` (`Import` / `Export`), `customDimensions.LegalEntity`, `customDimensions.environmentId`
> **Prerequisites:** F&O telemetry export to App Insights with DMF events enabled in LCS.

## What this dashboard tells you

Everything happening in F&O's Data Management Framework — imports vs exports, per-entity volumes and durations, errors by data project, unfinished runs, and outlier executions (by duration and record count). The headline KPI per data project: did it finish, how long did it take, how many records did it move, and what failed.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` / `_endTime` | every tile | `ago(7d)` / `now()` | Default window per file |
| `_dataProjectName` | several | `''` (= All) | Pass-through when empty |
| `_entityName` | several | `''` (= All) | Pass-through when empty |
| `_legalEntity` | several | `''` (= All) | Pass-through when empty |
| `_environmentId` | several | `''` (= All) | Pass-through when empty |

> Numbers 17, 21, 22 are intentionally skipped — they're spacer placeholders carried over from the upstream MS Learn / FastTrack source.

## Tile catalog

### Activity & inventory

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | All export activities | table | [`01-all-export-activities.kql`](01-all-export-activities.kql) | Recent DMF export runs |
| 02 | All import activities | table | [`02-all-import-activities.kql`](02-all-import-activities.kql) | Recent DMF import runs |
| 03 | Import vs export count (completed) | piechart | [`03-import-vs-export-count-completed.kql`](03-import-vs-export-count-completed.kql) | Completed-run split between imports and exports |
| 06 | All DMF events (Event ID 10000) | table | [`06-all-dmf-events-10000.kql`](06-all-dmf-events-10000.kql) | Raw view of the DMF event source |

### Volume & duration per entity

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 04 | Completed executions per entity | barchart | [`04-completed-executions-per-entity.kql`](04-completed-executions-per-entity.kql) | Which entities have the most completed executions |
| 05 | Total records per entity | barchart | [`05-total-records-per-entity.kql`](05-total-records-per-entity.kql) | Which entities have moved the most records |
| 08 | Total duration (sec) per entity × direction | table | [`08-total-duration-sec-per-entity-and-direction.kql`](08-total-duration-sec-per-entity-and-direction.kql) | Per-entity total elapsed time, import vs export |
| 13 | Avg record-processing duration by project | table | [`13-avg-record-processing-duration-by-data-project.kql`](13-avg-record-processing-duration-by-data-project.kql) | Avg ms per record per project — efficiency metric |

### Volume & duration per data project

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 09 | Data project execution timeline | timechart | [`09-data-project-execution-timeline.kql`](09-data-project-execution-timeline.kql) | When did each project run, over time |
| 14 | Total executions per data project | barchart | [`14-total-executions-per-data-project.kql`](14-total-executions-per-data-project.kql) | Run count per project |
| 15 | Total records per data project | barchart | [`15-total-records-per-data-project.kql`](15-total-records-per-data-project.kql) | Records moved per project |
| 16 | Total duration (sec) per data project | barchart | [`16-total-duration-sec-per-data-project.kql`](16-total-duration-sec-per-data-project.kql) | Total elapsed time per project |
| 19 | Avg #records per data project | barchart | [`19-avg-number-or-records-per-data-project.kql`](19-avg-number-or-records-per-data-project.kql) | Average run size per project |

### Outliers

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 07 | Executions by duration — top 100 | table | [`07-executions-by-duration-top-100.kql`](07-executions-by-duration-top-100.kql) | 100 longest DMF executions in window |
| 18 | Unfinished runs | table | [`18-unfinished-runs.kql`](18-unfinished-runs.kql) | Runs that started but haven't reported completion — stuck imports |
| 20 | Executions by #records — top 10 | table | [`20-executions-by-number-of-records-top-10.kql`](20-executions-by-number-of-records-top-10.kql) | 10 largest runs by record count |

### Errors

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 10 | Errors per data project | barchart | [`10-errors-per-per-project.kql`](10-errors-per-per-project.kql) | Error count grouped by project |
| 11 | All errors (limit 1000) | table | [`11-all-errors-limit-1000.kql`](11-all-errors-limit-1000.kql) | Raw error list |
| 12 | Errors trend timeline | timechart | [`12-errors-trend-timeline.kql`](12-errors-trend-timeline.kql) | Error count over time — release / regression signal |

## Flagship tile — paste & run

### Tile 09 · Data project execution timeline

**Viz:** timechart
**Source:** [`./09-data-project-execution-timeline.kql`](./09-data-project-execution-timeline.kql)

The single best "did the import run on schedule?" view. Each project gets a series; a missing line on a day = the import didn't fire.

### Tile 12 · Errors trend timeline

**Viz:** timechart
**Source:** [`./12-errors-trend-timeline.kql`](./12-errors-trend-timeline.kql)

The "did something regress today?" view. A step-up usually pairs with a release or an upstream-data change — drill via tile 10 (errors per project) and tile 11 (raw errors).

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `F&O Data Management Framework monitoring`.
2. Add your F&O App Insights resource as a data source.
3. Four pages:
   - **Activity & inventory** — 01, 02, 03, 06
   - **Volume per entity** — 04, 05, 08, 13
   - **Volume per project** — 09, 14, 15, 16, 19
   - **Outliers & errors** — 07, 10, 11, 12, 18, 20
4. Expose `_startTime`, `_endTime`, `_dataProjectName`, `_entityName`, `_legalEntity`, `_environmentId` as dashboard parameters.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-dmf-monitoring.md`](./DASHBOARD-dmf-monitoring.md). Regenerate the **Activity & inventory** and **Outliers & errors** pages in my F&O App Insights — cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace Procurement said the `VendorMaster` import didn't show new data this morning. Use this dashboard — start with tile 18 (unfinished runs) filtered to the project, then tile 09 to confirm whether it even started, then tile 11 for any errors logged."*

## Related dashboards

- [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md) — DMF runs on F&O batch — a starved batch framework will manifest as DMF runs not starting on schedule
- [`../errors/DASHBOARD-errors-triage.md`](../errors/DASHBOARD-errors-triage.md) — broader F&O exception triage; DMF errors often show up here too
- [`../custom/DASHBOARD-xpp-custom-signals.md`](../custom/DASHBOARD-xpp-custom-signals.md) — tile 06 of that dashboard cross-references DMF errors as events vs exceptions
