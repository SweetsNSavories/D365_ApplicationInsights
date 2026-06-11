# _shared/overview/

Cross-table starting points and integration plumbing.

## Files

| # | File | What it does |
|---|---|---|
| 01 | [`01-pageviews-top100.kql`](01-pageviews-top100.kql) | Top 100 most-viewed pages across all components |
| 02 | [`02-pageviews-by-operation-id.kql`](02-pageviews-by-operation-id.kql) | Walk all telemetry for a single `operation_Id` |
| 03 | [`03-loganalytics-azurediagnostics-output.kql`](03-loganalytics-azurediagnostics-output.kql) | Template for reading App Insights output from a Log Analytics workspace via `AzureDiagnostics` |

## Correlation columns quick-reference

| Column | Meaning |
|---|---|
| `operation_Id` | Trace ID — same value across every row of one end-to-end activity |
| `operation_ParentId` | Caller span ID — parent of this row |
| `id` | This row's span ID |
| `session_Id` | UCI session (model-driven) / portal session (Power Pages) |

Use `operation_Id` to join `pageViews` ↔ `requests` ↔ `dependencies` ↔ `exceptions` ↔ `traces` ↔ `customEvents` for one user action.
