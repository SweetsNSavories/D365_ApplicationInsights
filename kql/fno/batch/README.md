# `kql/fno/batch/` — D365 F&SCM Batch jobs

Telemetry around the F&O **batch framework** — server configuration, thread pools, task priority, throttling, infolog errors, and the Priority-Based Scheduling (PBS) queue.

## Telemetry shape

| Surface | Notes |
|---|---|
| `customEvents` | `name == "BatchThreadInfo"` carries thread-pool snapshots; `customDimensions.InfoMessage` is a JSON blob with `MaxThreadCount`, `ReservedNumberOfThreads`, `TaskQueueCount`, `CurrentBatchTasks` |
| `customEvents` | `name == "BatchTaskHistory"`, `"BatchTaskThrottled"`, `"BatchJobHistory"` describe per-task lifecycle |
| `exceptions` | Batch-task exceptions tag `customDimensions.BatchJobId`, `BatchTaskId`, `ExecutionMode = "Batch"` |
| `traces` | Infolog warnings/errors raised inside batch tasks |

Identify the AOS that ran a batch task with `cloud_RoleInstance`. Group an execution across child tasks via `customDimensions.BatchJobId`.

## Files

| File | Tile (upstream dashboard) |
|---|---|
| [01-batch-server-configuration.kql](01-batch-server-configuration.kql) | Batch server configuration |
| [02-batch-server-tasks-execution-spread.kql](02-batch-server-tasks-execution-spread.kql) | Batch server #tasks execution spread |
| [03-throttled-batch-tasks.kql](03-throttled-batch-tasks.kql) | Throttled batch tasks |
| [04-priority-distribution.kql](04-priority-distribution.kql) | Priority distribution |
| [05-available-batch-threads.kql](05-available-batch-threads.kql) | Available batch threads |
| [06-batch-execution-history.kql](06-batch-execution-history.kql) | Batch execution history |
| [07-throttled-batch-tasks-2.kql](07-throttled-batch-tasks-2.kql) | Throttled batch tasks (alt view) |
| [08-throttled-batch-tasks-3.kql](08-throttled-batch-tasks-3.kql) | Throttled batch tasks (alt view) |
| [09-batch-exceptions.kql](09-batch-exceptions.kql) | Batch exceptions |
| [10-batch-infolog-errors.kql](10-batch-infolog-errors.kql) | Batch Infolog Errors |
| [11-batch-exceptions-over-time.kql](11-batch-exceptions-over-time.kql) | Batch exceptions over time |
| [12-batch-infolog-errors-2.kql](12-batch-infolog-errors-2.kql) | Batch Infolog Errors (alt view) |
| [13-pbs-queue-sizes.kql](13-pbs-queue-sizes.kql) | PBS Queue sizes |

## Source

Extracted from the upstream Microsoft sample dashboard:
`Dashboards/AzureDataExplorer/Batch/ADE-Dashboard-D365FO-Monitoring-Batch.json` in
[microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) (MIT-licensed).
