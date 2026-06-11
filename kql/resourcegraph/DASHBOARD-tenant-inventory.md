# Dashboard — Power Platform tenant inventory (Azure Resource Graph)

> **For:** Power Platform admins, CoE owners, tenant-wide governance.
> **Signal:** [Azure Resource Graph](https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview) — `PowerPlatformResources` table.
> **Runtime:** **Azure Resource Graph Explorer**, NOT Application Insights / Log Analytics.
> **Pivot keys:** `type`, `properties.environment`, `properties.region`, `properties.owners`, `properties.connectionReferences[].connectorName`.

## What this dashboard tells you

A tenant-level inventory of every Power Platform asset — flows, agents, apps, connectors — with counts, owners, connector usage, and "what was created in the last 24 h". This is the **governance** view, not the runtime view; for runtime telemetry of any single asset, jump to the matching App Insights dashboard.

> **Runtime difference:** every tile below runs against **Azure Resource Graph**, not App Insights. Do not paste these into the Logs blade. Use [Azure Resource Graph Explorer](https://portal.azure.com/#blade/HubsExtension/ArgQueryBlade) or `az graph query -q "<paste>"`.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `<agentName>` | 06 | `'AssetManager Bot'` | Display name to search for |
| `<connectorId>` | 10 | `'shared_office365'` | ARG `connectorName` value |
| (none) | most tiles | — | Tenant-wide aggregates are parameter-free by design |

## Tile plan

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Total Power Platform resource count | stat | [`01-total-count.kql`](01-total-count.kql) | Single number — how many PP assets exist in this tenant |
| 02 | Breakdown by resource type | piechart | [`02-counts-by-type.kql`](02-counts-by-type.kql) | Flows vs apps vs agents vs … |
| 03 | Per-environment counts | barchart | [`03-counts-by-environment.kql`](03-counts-by-environment.kql) | Asset count grouped by Dataverse environment |
| 04 | Per-region counts | barchart | [`04-counts-by-region.kql`](04-counts-by-region.kql) | Asset count grouped by region |
| 05 | Top resource owners | barchart | [`05-top-owners.kql`](05-top-owners.kql) | Who owns the most assets (governance / risk focus) |
| 06 | Find a specific Copilot agent | table | [`06-find-agent.kql`](06-find-agent.kql) | Locate an agent by name |
| 07 | Items created in last 24 h | table | [`07-items-created-24h.kql`](07-items-created-24h.kql) | Fresh creation activity feed |
| 08 | Most-used connectors | barchart | [`08-top-connectors.kql`](08-top-connectors.kql) | Top connectors by usage count |
| 09 | Connector-count distribution | columnchart | [`09-connector-count-distribution.kql`](09-connector-count-distribution.kql) | Histogram of how many connectors each asset uses |
| 10 | Find resources using a given connector | table | [`10-find-resources-by-connector.kql`](10-find-resources-by-connector.kql) | All flows/apps using `<connectorId>` (e.g. for an outage RCA) |
| 11 | Connector usage per environment | table | [`11-connector-usage-by-env.kql`](11-connector-usage-by-env.kql) | Connector × environment matrix |

## Flagship tile — paste & run

### Tile 02 · Breakdown by resource type

**Viz:** piechart
**Source:** [`./02-counts-by-type.kql`](./02-counts-by-type.kql)

The single fastest "what does this tenant look like?" answer. A tenant heavily skewed to flows vs canvas apps suggests different risk/governance focus than the inverse.

### Tile 10 · Find resources using a given connector

**Viz:** table
**Source:** [`./10-find-resources-by-connector.kql`](./10-find-resources-by-connector.kql)

The blast-radius tile. Used most often when an underlying connector has a service incident (e.g. SharePoint, SQL) — substitute `<connectorId>` to enumerate every flow / app that may be impacted.

## Build in Azure Data Explorer dashboards

ARG queries are **not** ADX queries, so the standard ADX dashboards experience doesn't apply directly. Three options:

**Option A — Azure Resource Graph Explorer (recommended for ad-hoc).**

1. Portal → search **Resource Graph Explorer**.
2. Paste each `.kql` into the editor → **Run query**.
3. **Save query** with the tile name from the tile plan.
4. Saved queries are accessible from the **Saved queries** pane on the left.

**Option B — Azure Workbook over Resource Graph.**

1. Portal → **Azure Monitor → Workbooks → New**.
2. **+ Add → Add query → Data source: Azure Resource Graph**.
3. Paste each `.kql` → set the visualization (piechart / barchart / grid) per the **Viz** column.
4. Save the workbook.

**Option C — `az graph` in CI / scripts.**

```pwsh
az graph query -q "$(Get-Content kql\resourcegraph\02-counts-by-type.kql -Raw)"
```

Useful for nightly snapshots / CoE reporting.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-tenant-inventory.md`](./DASHBOARD-tenant-inventory.md). Run all 11 tiles in **Azure Resource Graph Explorer** (NOT App Insights) and summarize: total assets (tile 01), top type (tile 02), top owner (tile 05), top connector (tile 08), assets created in the last 24 h (tile 07)."*

Symptom-driven:

> *"@workspace SharePoint Online had an outage at 10:00 UTC. Use tile 10 with `<connectorId>` = `shared_sharepointonline` to list every flow and app that may have been impacted."*

Governance audit:

> *"@workspace I'm building a CoE report. Use tiles 01, 02, 03, 04, 05, 07 to produce a markdown summary of tenant inventory."*

## Related dashboards

- [`../powerautomate/DASHBOARD-flow-runs.md`](../powerautomate/DASHBOARD-flow-runs.md) — runtime view of flows (App Insights); ARG counts them, App Insights tells you which are running and failing
- [`../canvasapp/DASHBOARD-canvas-health.md`](../canvasapp/DASHBOARD-canvas-health.md) — runtime view of canvas apps

## Reference

- [Azure Resource Graph — query Power Platform resources](https://learn.microsoft.com/en-us/power-platform/admin/azure-resource-graph)
- [Resource Graph KQL reference](https://learn.microsoft.com/en-us/azure/governance/resource-graph/concepts/query-language)
