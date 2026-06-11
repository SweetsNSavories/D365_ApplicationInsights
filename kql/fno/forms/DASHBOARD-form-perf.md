# Dashboard — F&O form performance

> **For:** F&O functional consultants, users complaining about specific slow forms, performance optimization owners.
> **Signal:** `pageViews` (form opens), with `cloud_RoleName == "AOSService"` and `customDimensions` carrying form-context metadata.
> **Window:** 1 d hot, 7–30 d trends
> **Pivot keys:** `name` (form name), `customDimensions.LegalEntity`, `customDimensions.UserId`, duration percentiles
> **Prerequisites:** F&O telemetry export to App Insights with the page-view (form) event enabled in LCS.

## What this dashboard tells you

Which F&O forms are opened most often, which take the longest on average, and how their duration trends over time per legal entity / user. Use this to find the top 1-2 forms to optimize.

> **Provenance note:** these queries are partially duplicated in the [Analyze Application Insights data with KQL](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/lifecycle-services/analyze-application-insights-data) MS Learn doc. The folder here keeps each as a standalone file; the Learn doc weaves them into a tutorial.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` / `_endTime` | every tile | `ago(7d)` / `now()` | Default window per file |
| `_formName` | several | `''` (= All) | Pass-through when empty |
| `_legalEntity` | 04 | `''` (= All) | Pass-through when empty |
| `_userId` | several | `''` (= All) | Pass-through when empty |

## Tile catalog

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Top 20 most-opened forms | barchart | [`01-top-20-most-opened-forms.kql`](01-top-20-most-opened-forms.kql) | Which forms users open most often — usage facet |
| 02 | Form usage by longest avg duration | barchart | [`02-form-usage-by-longest-average-duration.kql`](02-form-usage-by-longest-average-duration.kql) | Forms ranked by avg open duration — perf facet |
| 03 | Form execution spread | columnchart | [`03-form-execution-spread.kql`](03-form-execution-spread.kql) | Distribution / histogram of execution times |
| 04 | Form execution by legal entity | barchart | [`04-form-execution-by-legal-entity.kql`](04-form-execution-by-legal-entity.kql) | Which company drives the form load |
| 05 | Form instance execution times | table | [`05-form-instance-execution-times.kql`](05-form-instance-execution-times.kql) | Per-instance durations (find outliers) |
| 06 | Form duration trend | timechart | [`06-form-duration-trend.kql`](06-form-duration-trend.kql) | Avg duration over time — regression signal |
| 07 | Form instance execution times (alt) | table | [`07-form-instance-execution-times-2.kql`](07-form-instance-execution-times-2.kql) | Alternative per-instance view (different pivot) |

## Flagship tile — paste & run

### Tile 02 · Form usage by longest average duration

**Viz:** barchart
**Source:** [`./02-form-usage-by-longest-average-duration.kql`](./02-form-usage-by-longest-average-duration.kql)

The single best "where should I focus performance work?" view. Cross-reference with tile 01 — a form that's both **slow and opened often** has the highest ROI on optimization; one that's slow but rarely opened can be deprioritised.

### Tile 06 · Form duration trend

**Viz:** timechart
**Source:** [`./06-form-duration-trend.kql`](./06-form-duration-trend.kql)

The "did it regress?" tile. A sudden step-up on one form usually corresponds to a release / customization import — pair with [`../slowqueries/DASHBOARD-slow-sql.md`](../slowqueries/DASHBOARD-slow-sql.md) tile 02 to see if a slow query showed up at the same time.

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `F&O form performance`.
2. Add your F&O App Insights resource as a data source.
3. Single page with all 7 tiles is fine.
4. Expose `_startTime`, `_endTime`, `_formName`, `_legalEntity`, `_userId` as dashboard parameters.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-form-perf.md`](./DASHBOARD-form-perf.md). Regenerate all 7 tiles in my F&O App Insights — cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace 'Form `CustTable` is slow today'. Use this dashboard — start with tile 06 filtered to `_formName='CustTable'` to confirm the trend, then tile 03 for the distribution shape, then tile 05 to see the slowest individual opens with full context."*

## Related dashboards

- [`../errors/DASHBOARD-errors-triage.md`](../errors/DASHBOARD-errors-triage.md) — slow forms often co-occur with exception spikes
- [`../slowqueries/DASHBOARD-slow-sql.md`](../slowqueries/DASHBOARD-slow-sql.md) — common root cause for slow forms is slow X++ SQL
- [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md) — when batch is starving threads, interactive forms slow down too
