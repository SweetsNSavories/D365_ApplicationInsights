# Live Dashboards: Run KQL, Show Results, Capture Observations

The `DASHBOARD-*.md` files in this repository are **dashboard specs and runbooks**. They are not the final dashboard by themselves.

Every KQL folder that has runnable tiles also has two generated live-dashboard files:

| File | What it does |
|---|---|
| `LIVE-DASHBOARD.json` | Machine-readable manifest with 10-15 tiles, query paths, visualization hints, runtime, and observation focus. |
| `LIVE-DASHBOARD.ipynb` | VS Code/Jupyter runbook that executes the manifest through the shared Python runner. |
| `live-output/index.html` | Committed dry-run preview page for the folder's live dashboard, with no customer data. |

A customer-facing dashboard is created in the customer's own Application Insights / Azure Data Explorer context. It must:

1. Run the KQL for each tile against the selected App Insights resource.
2. Display the returned rows or chart for that tile.
3. Capture observations from the returned data.
4. Flag zero-row tiles as instrumentation, time-window, table-name, or filter questions.
5. Establish exception and trace noise before calling something an incident signal.

## Where The Live Dashboard Runs

Use one of these runtime surfaces:

| Surface | Best for |
|---|---|
| **Azure Data Explorer dashboards** | Persistent visual dashboards with tiles that execute KQL. |
| **Application Insights Logs** | Ad hoc query execution and raw-row inspection. |
| **VS Code + Akusto Explorer / Kusto extension** | Copilot-assisted troubleshooting where Copilot opens linked `.kql`, runs it, and summarizes observations. |

The public GitHub repo stays generic. Customer-specific dashboard output, screenshots, query exports, and observations should go under a local `cases/` folder or another private customer workspace.

## Run The Packaged Live Dashboards

Install the Python dependencies once:

```pwsh
python -m pip install -r requirements-live-dashboard.txt
```

Dry-run any folder first. This checks that the manifest, query files, and output generation work without querying customer data, and it refreshes the committed preview page:

```pwsh
python tools\live_dashboard_runner.py --manifest kql\dataverse\LIVE-DASHBOARD.json --output kql\dataverse\live-output --dry-run
```

Run against an Application Insights resource. Write customer results to `live-dashboard-output/`, not the committed preview folder:

```pwsh
python tools\live_dashboard_runner.py --manifest kql\dataverse\LIVE-DASHBOARD.json --output kql\dataverse\live-dashboard-output --appinsights-resource-id "<resourceId>" --timespan-days 30
```

The HTML page heading displays the App Insights instance name inferred from `--appinsights-resource-id`, for example `App Insights: contoso-prod-ai`. If you query through a workspace or want a customer-friendly display label, add `--instance-name "<friendlyName>"`.

Run against a Log Analytics workspace instead:

```pwsh
python tools\live_dashboard_runner.py --manifest kql\dataverse\LIVE-DASHBOARD.json --output kql\dataverse\live-dashboard-output --workspace-id "<workspaceId>" --timespan-days 30
```

Run the Azure Resource Graph inventory dashboard:

```pwsh
python tools\live_dashboard_runner.py --manifest kql\resourcegraph\LIVE-DASHBOARD.json --output kql\resourcegraph\live-dashboard-output --subscriptions "<subscriptionId1>,<subscriptionId2>"
```

Each run writes local artifacts:

| Output | Purpose |
|---|---|
| `live-output/index.html` | Committed dry-run preview page for the folder. |
| `live-dashboard-output/index.html` | Rendered dashboard with live customer tile status, observations, and table previews. |
| `live-dashboard-output/observations.md` | Markdown observation log for the case notes. |
| `live-dashboard-output/results.json` | Structured result summary and row previews. |
| `live-dashboard-output/csv/tile-XX.csv` | Per-tile CSV exports. |

Only the dry-run `live-output/index.html` preview is committed. Keep `live-dashboard-output/` local or move it into a private customer case workspace.

You can run the same workflow from VS Code by opening a folder's `LIVE-DASHBOARD.ipynb`, setting `DRY_RUN = False`, and filling either `APPINSIGHTS_RESOURCE_ID`, `WORKSPACE_ID`, or `SUBSCRIPTIONS` depending on the manifest runtime.

## Copilot Prompt: Load The Live Dashboard Preview

Use this when you want GitHub Copilot to open the committed no-data preview first, then guide the real run:

> `@workspace Load the live dashboard preview at kql/<component>/live-output/index.html. Confirm the dashboard title, tile count, dry-run status, and current heading. Then open kql/<component>/LIVE-DASHBOARD.json and kql/<component>/LIVE-DASHBOARD.ipynb, explain what each tile will run, and tell me exactly what values I need to fill before running this against my App Insights resource. When I provide the resource ID, make sure the generated live dashboard heading includes the App Insights instance name. Do not treat the dry-run preview as customer evidence.`

For example:

> `@workspace Load kql/dataverse/live-output/index.html, then inspect kql/dataverse/LIVE-DASHBOARD.json and kql/dataverse/LIVE-DASHBOARD.ipynb. Walk me through how to turn this preview into a real customer run using my App Insights resource ID, and remind me that live customer output goes to kql/dataverse/live-dashboard-output/.`

Use this when you want Copilot to run the packaged notebook or manifest from VS Code agent mode:

> `@workspace Run the packaged live dashboard for kql/<component>. Use kql/<component>/LIVE-DASHBOARD.ipynb or tools/live_dashboard_runner.py. First dry-run it to refresh kql/<component>/live-output/index.html. Then, after I provide the App Insights resource ID or workspace ID, run it with output in kql/<component>/live-dashboard-output/, set or verify the App Insights instance name in the dashboard heading, and summarize live-dashboard-output/observations.md.`

## Copilot Prompt: Build A Live Dashboard

Use this when you want GitHub Copilot to go beyond listing files:

> `@workspace Build a live dashboard from kql/<component>/DASHBOARD-<name>.md. Do not stop at listing the .kql files. For each tile, open the linked .kql, run it through the Kusto / Akusto Explorer extension against my selected App Insights connection, render or describe the returned result, write 1-3 observations from the data, and list the next drill-down if the tile shows a spike, error, or zero rows.`

For a first-look dashboard on an unfamiliar resource:

> `@workspace Use kql/_shared/DASHBOARD-overview.md to create a live first-look dashboard. Run the all-table pulse, pageViews channel split, exception signal-vs-noise, top real exceptions, noisy trace/custom-event candidates, and ingestion-cost tiles. For each tile, summarize the result and write observations backed by returned rows.`

## Observations Template

For each tile, capture this:

```markdown
## Tile <number>: <title>

- Query: <path-to-kql>
- Time window: <window used>
- Result: <rows returned / chart shape / zero rows>
- Observation: <what the returned data shows>
- Noise handling: <filters applied, known noise removed, or none>
- Next drill-down: <operation_Id, session_Id, user, dependency, exception message, trace prefix, or component dashboard>
```

## Noise First, Then Signal

Exception and trace tables often contain repetitive platform/framework noise. Before diagnosing from those tables:

1. Run the shared exception noise queries in `kql/_shared/exceptions/`.
2. Build a `traces` baseline by `severityLevel`, message prefix, `operation_Name`, `cloud_RoleName`, and important `customDimensions`.
3. Keep proposed filters visible in the case notes.
4. Run the incident query both with and without the filters.
5. Only call out findings that survive raw-row inspection and a second signal.

Useful prompt:

> `@workspace Establish the exception and traces noise baseline before diagnosing. Show recurring known-noise patterns, propose visible filters, run the incident query with and without those filters, and keep only findings backed by returned rows and a second signal.`