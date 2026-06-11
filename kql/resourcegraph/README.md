# resourcegraph/

**Different runtime — NOT App Insights.** These run in Azure Resource Graph Explorer against the `PowerPlatformResources` table.

## Files

| # | File | What it does |
|---|---|---|
| 01 | [`01-total-count.kql`](01-total-count.kql) | Total Power Platform resource count in tenant |
| 02 | [`02-counts-by-type.kql`](02-counts-by-type.kql) | Breakdown by resource type |
| 03 | [`03-counts-by-environment.kql`](03-counts-by-environment.kql) | Per-environment counts |
| 04 | [`04-counts-by-region.kql`](04-counts-by-region.kql) | Per-region counts |
| 05 | [`05-top-owners.kql`](05-top-owners.kql) | Top resource owners |
| 06 | [`06-find-agent.kql`](06-find-agent.kql) | Find a specific Copilot agent by name |
| 07 | [`07-items-created-24h.kql`](07-items-created-24h.kql) | Items created in last 24 h |
| 08 | [`08-top-connectors.kql`](08-top-connectors.kql) | Most-used connectors |
| 09 | [`09-connector-count-distribution.kql`](09-connector-count-distribution.kql) | Distribution of connector counts per resource |
| 10 | [`10-find-resources-by-connector.kql`](10-find-resources-by-connector.kql) | Find every resource using a given connector |
| 11 | [`11-connector-usage-by-env.kql`](11-connector-usage-by-env.kql) | Connector usage per environment |

## How to run

Azure Resource Graph Explorer (Portal) or:

```pwsh
az graph query -q "<paste-here>"
```

These do **not** work in the App Insights blade or the workspace KQL editor — they target ARG only.

## Provenance

All eleven → [`MicrosoftDocs/power-platform`](https://github.com/MicrosoftDocs/power-platform) Resource Graph inventory samples.
