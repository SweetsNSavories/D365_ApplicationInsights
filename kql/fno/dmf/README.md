# `kql/fno/dmf/` — D365 F&SCM Data Management Framework (imports/exports)

Telemetry around the **Data Management Framework (DMF)** — bulk import/export jobs, per-entity record counts, staging vs target errors, and execution durations.

## Telemetry shape

| Surface | Notes |
|---|---|
| `customEvents` | `name startswith "DMF"` (e.g. `DMFImport`, `DMFExport`, `DMFEntityStagingComplete`, `DMFExecutionComplete`) |
| `customDimensions` keys | `ExecutionId`, `DataProjectName`, `EntityName`, `ExecutionMode`, `LegalEntity`, `BatchJobId`, `NumOfStagingNew`, `NumOfTargetNew`, `NumOfTargetUpdated`, `TotalNumberOfRecords`, `StagingErrorCount`, `TargetErrorCount`, `StagingStatus`, `TargetStatus`, `ErrorMessage`, `activityId`, `environmentId` |
| Direction discrimination | Use `iff(name startswith "DMFExport", "Export", "Import")` — see the inlined `allDMFEvents` view at the top of most files |

A "data project" is a named DMF configuration; an "execution" is one run of that project; an "activity" is a single entity-level slice within the execution.

## Files

| File | Tile (upstream dashboard) |
|---|---|
| [01-all-export-activities.kql](01-all-export-activities.kql) | All Export activities |
| [02-all-import-activities.kql](02-all-import-activities.kql) | All import activities |
| [03-import-vs-export-count-completed.kql](03-import-vs-export-count-completed.kql) | Import vs export count (completed) |
| [04-completed-executions-per-entity.kql](04-completed-executions-per-entity.kql) | Completed executions per entity |
| [05-total-records-per-entity.kql](05-total-records-per-entity.kql) | Total records per entity |
| [06-all-dmf-events-10000.kql](06-all-dmf-events-10000.kql) | All DMF events (10000) |
| [07-executions-by-duration-top-100.kql](07-executions-by-duration-top-100.kql) | Executions by duration (top 100) |
| [08-total-duration-sec-per-entity-and-direction.kql](08-total-duration-sec-per-entity-and-direction.kql) | Total duration (sec) per entity and direction |
| [09-data-project-execution-timeline.kql](09-data-project-execution-timeline.kql) | Data project execution timeline |
| [10-errors-per-per-project.kql](10-errors-per-per-project.kql) | Errors per project |
| [11-all-errors-limit-1000.kql](11-all-errors-limit-1000.kql) | All Errors (limit 1000) |
| [12-errors-trend-timeline.kql](12-errors-trend-timeline.kql) | Errors trend timeline |
| [13-avg-record-processing-duration-by-data-project.kql](13-avg-record-processing-duration-by-data-project.kql) | Avg record processing duration by Data project |
| [14-total-executions-per-data-project.kql](14-total-executions-per-data-project.kql) | Total executions per data project |
| [15-total-records-per-data-project.kql](15-total-records-per-data-project.kql) | Total records per data project |
| [16-total-duration-sec-per-data-project.kql](16-total-duration-sec-per-data-project.kql) | Total duration (sec) per data project |
| [18-unfinished-runs.kql](18-unfinished-runs.kql) | Unfinished runs |
| [19-avg-number-or-records-per-data-project.kql](19-avg-number-or-records-per-data-project.kql) | Avg number of records per data project |
| [20-executions-by-number-of-records-top-10.kql](20-executions-by-number-of-records-top-10.kql) | Executions by number of records (top 10) |

> Tile numbers 17, 21, 22 in the upstream dashboard are markdown/spacer tiles with no KQL.

## Source

Extracted from the upstream Microsoft sample dashboard:
`Dashboards/AzureDataExplorer/DMF/dashboard-D365FO-Monitoring-DMF.json` in
[microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) (MIT-licensed).
