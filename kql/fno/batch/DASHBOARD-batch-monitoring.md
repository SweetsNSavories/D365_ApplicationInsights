# Dashboard — F&O Batch monitoring

> **For:** D365 F&O technical consultants, BatchService admins, throttle/regression triage.
> **Signals:** `customMetrics` (batch configuration, thread availability), `customEvents` (batch task execution, infolog), `exceptions` (batch errors)
> **Window:** 1 d hot, 7–30 d trends
> **Pivot keys:** `cloud_RoleName` (`BatchService`), `cloud_RoleInstance` (specific AOS), `customDimensions.LegalEntity`, `customDimensions.environmentId`
> **Prerequisites:** F&O telemetry export to customer-owned App Insights ([Lifecycle Services telemetry setup](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/lifecycle-services/application-insights-overview)).

## What this dashboard tells you

The Batch framework's heartbeat — configuration, available threads, task execution spread, throttling events, recent failures, and the PBS (Performance Batch Server / scaled-out) queue. Use this when business users complain that "jobs aren't running" or "everything got slow at 3 AM".

> **F&O specifics:** F&O telemetry is point-to-point to a customer-owned App Insights, distinct from the tenant-wide Power Platform pipeline. Triage facets to always include: `cloud_RoleName` (`AOSService` / `BatchService` / `DIXFService`), `cloud_RoleInstance` (the specific AOS), `customDimensions.ExecutionMode`, `customDimensions.LegalEntity`, `customDimensions.environmentId`. Dashboard parameters in every F&O tile are `let` bindings near the top with safe defaults — empty string is the pass-through value because upstream queries use the `isempty(<var>) or <Column> == <var>` idiom.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `_startTime` / `_endTime` | every tile | `ago(7d)` / `now()` | Default window per file |
| `_legalEntity` | several | `''` (= All) | Pass-through when empty |
| `_environmentId` | several | `''` (= All) | Pass-through when empty |
| `_cloudRoleInstance` | several | `''` (= All) | Filter to one AOS instance |

## Tile plan

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Batch server configuration | table | [`01-batch-server-configuration.kql`](01-batch-server-configuration.kql) | What `customMetrics` says about each batch server's max-threads / priority config |
| 02 | Batch tasks — execution spread | columnchart | [`02-batch-server-tasks-execution-spread.kql`](02-batch-server-tasks-execution-spread.kql) | How tasks distribute across batch servers (hotspots) |
| 03 | Throttled batch tasks | table | [`03-throttled-batch-tasks.kql`](03-throttled-batch-tasks.kql) | Tasks the batch framework throttled |
| 04 | Task priority distribution | piechart | [`04-priority-distribution.kql`](04-priority-distribution.kql) | Share of tasks by priority level |
| 05 | Available batch threads | timechart | [`05-available-batch-threads.kql`](05-available-batch-threads.kql) | Thread headroom over time — capacity ceiling check |
| 06 | Batch execution history | table | [`06-batch-execution-history.kql`](06-batch-execution-history.kql) | Recent batch task executions with status |
| 07 | Throttled batch tasks (alt) | table | [`07-throttled-batch-tasks-2.kql`](07-throttled-batch-tasks-2.kql) | Alternative throttle view (per-task) |
| 08 | Throttled batch tasks (per-class) | table | [`08-throttled-batch-tasks-3.kql`](08-throttled-batch-tasks-3.kql) | Throttle counts grouped by class |
| 09 | Batch exceptions | table | [`09-batch-exceptions.kql`](09-batch-exceptions.kql) | `exceptions` filtered to `cloud_RoleName == "BatchService"` |
| 10 | Batch infolog errors | table | [`10-batch-infolog-errors.kql`](10-batch-infolog-errors.kql) | X++ infolog errors raised from batch context |
| 11 | Batch exceptions over time | timechart | [`11-batch-exceptions-over-time.kql`](11-batch-exceptions-over-time.kql) | Exception trend timeline |
| 12 | Batch infolog errors (alt) | table | [`12-batch-infolog-errors-2.kql`](12-batch-infolog-errors-2.kql) | Alternative infolog view |
| 13 | PBS queue sizes | timechart | [`13-pbs-queue-sizes.kql`](13-pbs-queue-sizes.kql) | Priority-Based Scheduling queue depth over time |

## Flagship tile — paste & run

### Tile 05 · Available batch threads

**Viz:** timechart
**Source:** [`./05-available-batch-threads.kql`](./05-available-batch-threads.kql)

The capacity-ceiling check. When available threads sit at zero for hours, every new job queues — pair with tile 13 (PBS queue) to see the backlog and tile 01 to confirm thread config matches the AOS SKU.

### Tile 13 · PBS queue sizes

**Viz:** timechart
**Source:** [`./13-pbs-queue-sizes.kql`](./13-pbs-queue-sizes.kql)

The "things are queuing" tile. A monotonically rising queue means producers > consumers — either bump batch threads (capacity) or fix the consuming class.

## Build in Azure Data Explorer dashboards

1. Create dashboard `F&O Batch monitoring`.
2. Add your F&O-owned App Insights resource as a data source.
3. Three pages:
   - **Capacity** — 01, 02, 04, 05, 13
   - **Throttling** — 03, 07, 08
   - **Failures** — 06, 09, 10, 11, 12
4. Expose `_startTime`, `_endTime`, `_legalEntity`, `_environmentId`, `_cloudRoleInstance` as dashboard parameters.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-batch-monitoring.md`](./DASHBOARD-batch-monitoring.md). Build a live dashboard for all 13 tiles in my F&O App Insights resource — cluster URI `<...>`, database `<...>`. Default `_legalEntity` and `_environmentId` to empty (= All)."*

Symptom-driven:

> *"@workspace 'Batch jobs are running hours late since this morning'. Use this dashboard — start with 05 to see if we ran out of threads, then 13 for queue depth, then 09 and 10 for any new errors."*

## Related dashboards

- [`../dmf/DASHBOARD-dmf-monitoring.md`](../dmf/DASHBOARD-dmf-monitoring.md) — DMF imports/exports run on the batch framework — a DMF spike can starve batch
- [`../errors/DASHBOARD-errors-triage.md`](../errors/DASHBOARD-errors-triage.md) — batch failures often co-occur with broader F&O exception spikes
- [`../slowqueries/DASHBOARD-slow-sql.md`](../slowqueries/DASHBOARD-slow-sql.md) — slow SQL inside batch is a common root cause for "everything is queuing"
