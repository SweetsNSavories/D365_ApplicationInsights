# Contributing

Thanks for contributing! This repo is a query library, so the bar is small: keep queries **standalone**, **runnable**, and **vendor-neutral**.

## Before you submit

- [ ] The query runs as-is when pasted into an App Insights Logs blade (no missing `let` imports, no broken references).
- [ ] All customer-specific values use the [placeholder convention](#placeholder-convention).
- [ ] The file has a `// Source:` header.
- [ ] It lands in the right folder (see [AGENTS.md](AGENTS.md#how-to-help-the-user) for routing).
- [ ] The folder's `README.md` table has a new row pointing at your file.
- [ ] No real GUIDs, user IDs, URLs, resource names, or tenant identifiers.

## File header

Every `.kql` must start with:

```kql
// Source: <repo or doc> / <path-on-source>
// (Optional) Original (if rewritten): <inline link or note>
// (One-line description of what the query answers.)
<query>
```

For locally authored queries (not from an upstream repo), use:

```kql
// Source: Locally authored (generic Power Platform App Insights queries)
```

## Naming

- Lowercase, dash-separated.
- Two-digit numeric prefix per folder, sequential (`01-…`, `02-…`).
- Describe what the query **answers**, not how it works.
  - Good: `04-exceptions-top10.kql`, `12-anomaly-traffic-drop-est-business-hours-30d.kql`
  - Avoid: `make-series-test.kql`, `query2.kql`

## Folder placement

| Query type | Folder |
|---|---|
| Single-component | `kql/<component>/` |
| Time-series version of a single-component query | `kql/<component>/timelines/` |
| Spans multiple components or compares them | `kql/_shared/timelines/` |
| Reusable lambda / noise filter | `kql/_shared/<topic>/` |
| Azure Resource Graph (NOT App Insights) | `kql/resourcegraph/` |
| Generic `traces`-table skeleton | `kql/platform-traces/` |

See [`AGENTS.md`](AGENTS.md) for the full component map.

## Style rules

- **Inline shared lambdas** — copy/paste, don't `let _foo = cluster(...)`. A user must be able to paste a single `.kql` into the portal and run it.
- **Time defaults** — use `ago(7d)` or `ago(30d)`. Don't hard-code absolute dates except in worked examples (and mark them as placeholder).
- **Column case** — App Insights classic schema uses camelCase (`timestamp`, `customDimensions`, `operation_Id`, `session_Id`). Don't invent column names.
- **`parse_json` once** — bind to a variable (`extend cd = parse_json(customDimensions)`), then project `cd.foo`.
- **`render`** — include when the query produces a chart-worthy shape. `timechart` for time series, `anomalychart` when using `series_decompose_anomalies`, `piechart` for top-N breakdowns.

## Placeholder convention

| Looks like | Means |
|---|---|
| `[userId]`, `[sessionIdHere]`, `[Plugin name here]` | Customer-supplied value |
| `<URLHere>`, `<resourceId>` | Customer-supplied value (alt notation) |
| `00aa00aa-bb11-cc22-dd33-44ee44ee44ee` | Obvious-fake GUID — substitute with a real one |
| `// Replace …` | Inline instruction immediately above the literal to swap |

## What's out of scope

- Bicep / ARM / Terraform for provisioning App Insights.
- Azure Workbooks, Grafana, Power BI dashboards.
- Customer-specific tuning. Generic queries only; document tuning knobs as comments.

## License

By submitting a PR you agree your contribution is licensed under [MIT](LICENSE).
