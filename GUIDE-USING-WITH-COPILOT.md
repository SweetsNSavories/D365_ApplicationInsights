# Use this repo with VS Code + Akusto Explorer + GitHub Copilot

A customer-facing guide for setting up VS Code, running the KQL query library, regenerating dashboards, and keeping troubleshooting evidence organized while GitHub Copilot helps with the investigation.

> Audience: anyone diagnosing a Dynamics 365 or Power Platform issue from Application Insights data — Dataverse admins, MDA / Power Pages devs, F&O technical consultants, Customer Service supervisors, and the partners who help them.

---

## What this corpus is

A library of **standalone KQL files** for Microsoft Dynamics 365 and Power Platform telemetry that lands in Azure Application Insights. Each `.kql` file is paste-and-run — no project setup, no shared lambdas you have to glue together. See [`README.md`](README.md) and [`kql/README.md`](kql/README.md) for the folder layout and provenance.

Alongside the `.kql` files, every folder ships a **`DASHBOARD-*.md` file** that catalogs the related queries as a single dashboard:

- What persona the dashboard is for
- Which App Insights signal it reads
- The list of tiles, each with **viz type** (table / timechart / piechart / barchart / scatterchart / columnchart / stat)
- The flagship "paste-and-run" tile inlined as KQL
- Steps to (re)generate the dashboard in Azure Data Explorer dashboards
- Copilot prompts to drive the whole thing from chat

The dashboard markdown is **self-contained context for GitHub Copilot**. Drop one file into Copilot Chat, ask "regenerate this in my App Insights", and Copilot can walk every tile.

---

## One-time setup

Before you start, gather:

- VS Code on the workstation where you will run the investigation.
- Access to this repository, either cloned from GitHub or provided as a workspace folder.
- The Application Insights resource name, subscription ID, resource group, and tenant that contains the D365 / Power Platform telemetry.
- A Microsoft Entra account with at least **Reader** and **Monitoring Reader** on the Application Insights resource.
- A GitHub Enterprise or personal GitHub account with GitHub Copilot enabled.
- Optional: Power Platform environment access if the case includes solution exports or customization review.

### 1. Clone the repo

```pwsh
git clone https://github.com/<your-org>/<this-repo>.git
cd <this-repo>
code .
```

### 2. Install the VS Code extensions

Required:

| Extension | Marketplace ID | Why |
|---|---|---|
| **Akusto Explorer / Kusto** | `ms-vscode.kusto-client` or the Kusto extension approved by your org | Run KQL against Azure Data Explorer / Application Insights / Log Analytics clusters from inside VS Code. Gives you syntax highlight on `.kql`, IntelliSense on tables and columns, and a results grid. |
| **GitHub Copilot Chat** | `github.copilot-chat` | The chat surface that reads the dashboard markdown + linked `.kql` files and writes / debugs queries with you. |

Useful when available:

| Extension / tool | Why |
|---|---|
| **Power Platform Tools** (`microsoft-IsvExpTools.powerplatform-vscode`) | Inspect Dataverse/Power Platform solution exports, use PAC CLI workflows, and compare solution components with telemetry findings. |
| **Microsoft Learn docs from Copilot** | Ask Copilot to verify telemetry meaning, table names, and feature behavior against Microsoft Learn while you troubleshoot, when documentation tools are available in your environment. |

Install the required extensions, then sign in:

- **Akusto Explorer / Kusto** → Command Palette → `Kusto: Add Connection` → paste the App Insights cluster URI (see next step).
- **Azure tenant access** → sign in with the customer/target tenant account that can read the App Insights resource. For cross-tenant work, make sure the selected tenant is the one that owns the subscription.
- **Copilot Chat** → status-bar Copilot icon → sign in with the GitHub Enterprise or personal GitHub account that has Copilot entitlements.

Keep the identities clear: the Microsoft Entra sign-in controls telemetry access, while the GitHub sign-in controls Copilot access. They may be different accounts.

### 3. Connect Kusto to your Application Insights resource

App Insights resources are queryable as Azure Data Explorer clusters via a proxy URI:

```
https://ade.applicationinsights.io/subscriptions/<subscriptionId>/resourcegroups/<resourceGroup>/providers/microsoft.insights/components/<appInsightsName>
```

The database name is the App Insights resource name itself.

1. Command Palette → `Kusto: Add Connection`.
2. Paste the URI above (substitute your IDs).
3. Pick **Microsoft Entra (Azure AD) Interactive** auth and sign in with an account that has at least **Reader** + **Monitoring Reader** on the App Insights resource.
4. The new cluster shows up under the Kusto sidebar; expand to find your database and the standard tables (`requests`, `dependencies`, `pageViews`, `exceptions`, `customEvents`, `customMetrics`, `traces`, `browserTimings`, `availabilityResults`).

> **Workspace-based App Insights?** If the App Insights resource is wired into a Log Analytics workspace, you have two options:
> 1. Keep using the cluster URI above (works for both classic and workspace-based) — table names stay as `requests`, `dependencies`, …
> 2. Connect Kusto directly to the Log Analytics workspace cluster — table names become `AppRequests`, `AppDependencies`, … See the mapping table in [`kql/README.md`](kql/README.md#tested-against).

### 4. Verify with a one-line probe

Open any `.kql` file in this repo, for example [`kql/_shared/timelines/06-all-tables-pulse-24h.kql`](kql/_shared/timelines/06-all-tables-pulse-24h.kql). Hit **Run Query** from the Kusto extension (`Ctrl+Shift+E` by default) - you should see a results grid in the Output pane. If it returns rows, you're connected.

Useful commands and prompts:

| What you need | Command / prompt |
|---|---|
| Add telemetry connection | Command Palette → `Kusto: Add Connection` |
| Run the active query | Select KQL, then **Run Query** / `Ctrl+Shift+E` |
| Preview a markdown guide or dashboard | Open the `.md` file, then press `Ctrl+Shift+V` (`Markdown: Open Preview`) |
| Open Copilot Chat | Command Palette → `GitHub Copilot: Open Chat` |
| Regenerate a dashboard | `@workspace Use kql/<component>/DASHBOARD-<name>.md to regenerate this dashboard in my App Insights resource. Use the Kusto extension to run every linked .kql and tell me the suggested visualization for each tile.` |
| Start troubleshooting from a symptom | `@workspace I am seeing <symptom>. Pick the right dashboard from AGENTS.md, run the broad health tiles first, then drill into raw rows and explain what is verified.` |

---

## How to use the dashboards

Every folder under `kql/` has at least one `DASHBOARD-*.md` file. Open one — for example [`kql/dataverse/DASHBOARD-plugin-and-webapi-health.md`](kql/dataverse/DASHBOARD-plugin-and-webapi-health.md) — and you'll see:

- A short "What this tells you" section
- A **Parameters** table (placeholders to fill before running — `_startTime`, user IDs, app modules, etc.)
- A **Tile catalog** table — every query in the folder, with the viz the tile should render and a one-line "what it answers"
- A **Flagship tile** with the query inlined for instant paste-and-run
- **(Re)generate in Azure Data Explorer dashboards** steps
- **Copilot prompts** for chat-driven regeneration and troubleshooting
- Links to **Related dashboards**

Use `Ctrl+Shift+V` to preview the dashboard markdown in VS Code. You can read it as a tutorial, or hand it to Copilot Chat as context. When viewing results, start from the broad health tiles, then drill into raw rows only after a trend, spike, error family, user, session, operation, or resource ID stands out. Treat a zero-row tile as a signal to verify instrumentation, time range, table naming, and filters before concluding that the problem is absent.

---

## Core Copilot workflows

### Workflow A — "Regenerate this dashboard in my App Insights"

The dashboard markdown describes everything Copilot needs.

1. In VS Code, open the dashboard markdown (e.g. `kql/mobile/DASHBOARD-fs-mobile-offline.md`).
2. Open Copilot Chat (Ctrl+Alt+I).
3. Type:

   > `@workspace Use this dashboard markdown to regenerate the tiles in my App Insights resource. My cluster URI is <...>, database is <...>. For each tile in the catalog, run the linked .kql, tell me which viz to pick, and flag any tile that returns zero rows so I know what's not instrumented.`

4. Copilot will:
   - Open each linked `.kql` file via `@workspace`
   - Substitute the parameters you've put in the **Parameters** section
   - Run the query through the Kusto extension
   - Suggest the viz from the catalog's **Viz** column

You can also ask Copilot to **export the whole thing as an Azure Data Explorer dashboard JSON** that you import via the ADX dashboards UI — the tile metadata is all there in the markdown.

For hands-on execution, be explicit that Copilot should use the VS Code Kusto / Akusto Explorer connection rather than just explaining the query:

> `@workspace Open the linked .kql files from this DASHBOARD markdown, use the Kusto / Akusto Explorer extension to run each query against my selected App Insights connection, capture which rows came back, and tell me how to configure the chart for each tile.`

### Workflow B — "I'm seeing X — walk me through diagnosing it"

The dashboards are also a self-learning troubleshooting corpus. Use the dashboard markdown as a map.

1. Pick the most likely component folder ([`kql/README.md`](kql/README.md) is the routing index — also see [`AGENTS.md`](AGENTS.md)).
2. Open that folder's dashboard markdown.
3. Ask Copilot Chat:

   > `@workspace I'm seeing <symptom — e.g. "slow case form loads only for users in Brazil since Tuesday">. Use #DASHBOARD-uci-form-perf.md to pick the right tiles in order, run them, and explain the findings.`

4. Copilot will walk the catalog from the most general tile (volume / health) to the most specific (slowest pages / users / geos), running each query and summarizing.

### Workflow C — "Start a local case folder"

For customer-specific troubleshooting, keep evidence out of the reusable `kql/` corpus. Use a local `cases/` folder for screenshots, customer-provided exports, query outputs, and running notes. The folder is ignored by Git in this repo.

Ask Copilot:

> `@workspace Start a new local case folder under cases/CASE-<customer-or-ticket>-<yyyymmdd>-<short-symptom>. Create README.md with sections for symptom, scope, tenant/resource placeholders, timeline, evidence, queries run, findings, false positives ruled out, open questions, and next steps. Add subfolders diagnostics/, screenshots/, telemetry/, queries/, results/, solution/, and notes/. Do not put real customer identifiers into reusable kql/ files.`

Suggested local layout:

```text
cases/
└── CASE-<customer-or-ticket>-<yyyymmdd>-<short-symptom>/
   ├── README.md
   ├── diagnostics/
   ├── screenshots/
   ├── telemetry/
   ├── queries/
   ├── results/
   ├── solution/
   └── notes/
```

If the customer gives you a solution zip or code export, put it under `solution/`, unzip it locally, and ask Copilot to inspect it with the Power Platform Tools extension or PAC CLI context. Then correlate what is in the solution, such as plug-ins, flows, web resources, forms, or PCF controls, with telemetry from the matching dashboard.

### Workflow D — "Start discovery from telemetry"

When the symptom is vague, begin with the shared overview dashboard before jumping into a component folder.

Ask Copilot:

> `@workspace Start discovery for this App Insights resource. Use kql/_shared/DASHBOARD-overview.md first. Run the all-table pulse, pageViews channel split, noise-filtered exception trend, top requests/dependencies, and ingestion-cost tiles. Summarize only findings that are backed by returned rows, then recommend the next component dashboard.`

After discovery, pivot to the component folder that matches the strongest signal. For example, `pageViews` with `customDimensions.appModule` points to Model-Driven Apps, `customDimensions.PortalId` points to Power Pages, flow telemetry points to Power Automate, and F&O telemetry should stay under `kql/fno/`.

If the customer gives you a known value, start there and save the case-specific probe locally:

> `@workspace Investigate <operation_Id/session_Id/requestId/conversationId/flowRunId/pluginTypeName/AppSessionID> for this case. Walk the relevant tables, save any case-specific KQL under cases/<case>/queries/, summarize the returned rows, and list what still needs cross-verification.`

Encourage creative troubleshooting, but keep it evidence-led:

> `@workspace Be creative but cautious. Give me three plausible hypotheses for this symptom, one query that can prove or disprove each, and the expected signal. Run the queries, discard weak hypotheses, and keep only findings backed by returned rows.`

---

## Optional case tooling

Some cases need docs or solution artifacts alongside telemetry. Use these only when they are available and approved for the engagement:

| Tool | Use it for |
|---|---|
| **Microsoft Learn docs through Copilot** | Verify table semantics, telemetry setup, feature behavior, and command syntax before finalizing a finding. |
| **Power Platform Tools + PAC CLI** | Authenticate to an environment, inspect solution metadata, and unpack solution zips for local analysis. |
| **VS Code search** | Search unpacked solution XML, plugin names, web resources, form IDs, flow names, JavaScript handlers, or PCF controls found in telemetry. |

Example terminal commands when a solution zip is part of the case:

```pwsh
pac auth create --url https://<org>.crm.dynamics.com
pac solution unpack --zipfile cases/<case>/solution/<solution>.zip --folder cases/<case>/solution/unpacked
```

Then ask Copilot:

> `@workspace Search cases/<case>/solution/unpacked for the plugin, flow, form, web resource, or PCF names found in telemetry. Connect the solution metadata back to the KQL evidence and list anything that remains unverified.`

### Useful Copilot vocabulary

| When you say… | …Copilot does |
|---|---|
| `@workspace #DASHBOARD-….md` | Loads the dashboard markdown as context |
| `Use the Kusto extension to run …` | Triggers query execution via the Kusto extension |
| `Apply the placeholder convention from kql/README.md` | Substitutes `[likeThis]` / fake-GUID tokens |
| `Filter out noise — see _shared/exceptions/02-known-noise-filter.kql` | Wraps exception queries in the documented noise filter |
| `Disambiguate pageViews per kql/_shared/timelines/01-…` | Splits MDA vs Portal vs F&O channels correctly |
| `Walk operation_Id end to end` | Joins `requests` + `dependencies` + `exceptions` for one correlation |
| `Verify this against Microsoft Learn` | Uses available docs/MCP tools to check table meaning, feature behavior, or setup docs |
| `Inspect the solution export in cases/.../solution/` | Uses local files plus Power Platform tooling to correlate app customizations with telemetry |
| `Establish exception and trace noise first` | Builds a baseline of recurring low-value errors/traces before looking for the real signal |

---

## Verification discipline

Copilot is a helper, not the source of truth. Before you share a conclusion with a customer:

1. Re-run the query with a wider and narrower time window.
2. Open sample raw rows behind every chart or summary.
3. Cross-check the same hypothesis with at least one second signal, such as `requests` plus `exceptions`, `pageViews` plus `dependencies`, or a dashboard tile plus a raw correlation query.
4. Verify table names and feature behavior against Microsoft Learn when schema or product behavior is unclear.
5. Keep asking Copilot to remove false positives until the finding is specific, reproducible, and tied to concrete rows.

Customer identifiers, screenshots, exports, and case notes belong in `cases/` or another private workspace. Only sanitized, reusable KQL should move back into `kql/`.

### Establish noise before diagnosis

Many D365 and Power Platform environments produce recurring exception and trace rows that are not the incident you are chasing. Do this before spending time on a spike:

1. Run the shared exception noise queries first: [`kql/_shared/exceptions/01-noise-catalog-breakdown-7d.kql`](kql/_shared/exceptions/01-noise-catalog-breakdown-7d.kql), [`kql/_shared/exceptions/04-exceptions-signal-vs-noise-30d.kql`](kql/_shared/exceptions/04-exceptions-signal-vs-noise-30d.kql), and [`kql/_shared/exceptions/06-noise-discovery-candidates-7d.kql`](kql/_shared/exceptions/06-noise-discovery-candidates-7d.kql).
2. For `traces`, start with a top-N baseline by `severityLevel`, message prefix, `operation_Name`, `cloud_RoleName`, and important `customDimensions`. Mark repetitive health checks, expected retries, framework chatter, and old known-noise strings in the case notes.
3. Ask Copilot to summarize what was filtered out and why. Do not hide filters; keep them visible in the case-specific query so another reviewer can challenge them.
4. Re-run the symptom query with the noise removed, then inspect raw rows behind the remaining top errors or trace messages.

Useful prompt:

> `@workspace Before diagnosing this incident, establish the exception and traces noise baseline for the last 30 days. Identify recurring known-noise patterns, show the filters you propose, then run the incident query with and without those filters so we do not waste time on false positives.`

---

## Extending the corpus

When you discover a new query that's broadly useful:

1. Drop the `.kql` into the right folder (see [`AGENTS.md`](AGENTS.md) — "Repository layout" + "Editing rules").
2. Preserve the `// Source:` header.
3. Add a row to that folder's `README.md` table.
4. Add a row to the matching `DASHBOARD-*.md` **Tile catalog** (or open a new one for a fresh category).
5. Open a PR — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

Copilot is great at scaffolding new dashboards too:

> `@workspace I just added kql/mycomponent/. Generate a DASHBOARD-mycomponent.md following the structure of kql/dataverse/DASHBOARD-plugin-and-webapi-health.md.`

---

## Troubleshooting the tooling

| Symptom | Fix |
|---|---|
| Kusto extension shows `No connection found` | Re-run `Kusto: Add Connection`. The cluster URI must start with `https://ade.applicationinsights.io/subscriptions/…` for App Insights resources. |
| Query returns `No tables found` | You're connected to the wrong database. The database name is the App Insights resource name. |
| Query runs but returns zero rows | (a) Time window is too narrow — bump `ago(7d)` to `ago(30d)`. (b) The component isn't sending telemetry — check the onboarding doc linked in the folder's README. (c) You hit the workspace-based vs classic table-name mismatch — see [`kql/README.md`](kql/README.md#tested-against). |
| `SemanticException: 'tableName' could not be resolved` | Classic-vs-workspace table naming. Try the `App*` prefix variant. |
| Copilot says "I can't read that file" | Re-open the file in the editor or prefix the request with `@workspace #filename`. |
| Copilot sign-in is unavailable | Sign in with the GitHub Enterprise or personal account that has Copilot enabled for this VS Code profile. |
| Wrong Azure tenant or authentication loop | Sign out of Azure in VS Code (`Azure: Sign Out`), then `Kusto: Add Connection` again and choose the tenant that owns the subscription. |
| Power Platform solution export is hard to inspect | Install Power Platform Tools, then keep the zip and extracted files under the local case folder's `solution/` directory. |

---

## What's intentionally not in this repo

- **Provisioning code** — no Bicep / ARM / Terraform for Application Insights. Use the upstream Microsoft docs.
- **Workbooks / Grafana JSON** — out of scope. The dashboards here are markdown catalogs that you (or Copilot) wire into Azure Data Explorer dashboards.
- **Customer-specific data** — every query uses placeholders; never commit real org IDs / user IDs / subscription IDs. See the placeholder convention in [`kql/README.md`](kql/README.md#placeholder-convention).
- **Live executable agents** — this is a knowledge corpus. The Copilot prompts are examples that guide your own GitHub Copilot Chat session.

---

## Index of dashboards

| Component | Dashboard | What it covers |
|---|---|---|
| Cross-component | [`kql/_shared/DASHBOARD-overview.md`](kql/_shared/DASHBOARD-overview.md) | First-look pulse, channel split, exception noise, ingestion cost |
| Dataverse | [`kql/dataverse/DASHBOARD-plugin-and-webapi-health.md`](kql/dataverse/DASHBOARD-plugin-and-webapi-health.md) | Plug-ins, Web API, SDK dependencies, server exceptions |
| Model-Driven Apps | [`kql/modeldrivenapp/DASHBOARD-uci-form-perf.md`](kql/modeldrivenapp/DASHBOARD-uci-form-perf.md) | UCI page loads, form perf, browser/device/geo, Monitor tool |
| Power Pages | [`kql/powerpages/DASHBOARD-portal-perf.md`](kql/powerpages/DASHBOARD-portal-perf.md) | Portal page perf, anonymous vs authenticated |
| Canvas Apps | [`kql/canvasapp/DASHBOARD-canvas-health.md`](kql/canvasapp/DASHBOARD-canvas-health.md) | Canvas sessions, slowest screens |
| Power Automate | [`kql/powerautomate/DASHBOARD-flow-runs.md`](kql/powerautomate/DASHBOARD-flow-runs.md) | Flow runs, action / trigger failures, billable-action leaderboards |
| Power Apps Mobile | [`kql/mobile/DASHBOARD-fs-mobile-offline.md`](kql/mobile/DASHBOARD-fs-mobile-offline.md) | Field Service Mobile offline sync — summary / errors / perf / payload / details |
| Conversation Diagnostics | [`kql/conversationdiagnostics/DASHBOARD-conversation-routing.md`](kql/conversationdiagnostics/DASHBOARD-conversation-routing.md) | Customer Service / Contact Center unified routing — fallback, overflow, CSR rejections, point-in-time rep state |
| F&O · Batch | [`kql/fno/batch/DASHBOARD-batch-monitoring.md`](kql/fno/batch/DASHBOARD-batch-monitoring.md) | Batch framework, threads, throttling, infolog errors, PBS queue |
| F&O · DMF | [`kql/fno/dmf/DASHBOARD-dmf-monitoring.md`](kql/fno/dmf/DASHBOARD-dmf-monitoring.md) | Data Management Framework imports / exports / errors |
| F&O · Errors | [`kql/fno/errors/DASHBOARD-errors-triage.md`](kql/fno/errors/DASHBOARD-errors-triage.md) | Exceptions by execution mode / legal entity / user |
| F&O · Forms | [`kql/fno/forms/DASHBOARD-form-perf.md`](kql/fno/forms/DASHBOARD-form-perf.md) | Form open frequency and duration |
| F&O · Slow SQL | [`kql/fno/slowqueries/DASHBOARD-slow-sql.md`](kql/fno/slowqueries/DASHBOARD-slow-sql.md) | AOS-surfaced slow queries |
| F&O · X++ Custom | [`kql/fno/custom/DASHBOARD-xpp-custom-signals.md`](kql/fno/custom/DASHBOARD-xpp-custom-signals.md) | X++ custom telemetry — UserLogOn, X++ exceptions, trace severity |
| Commerce | [`kql/fno/commerce/DASHBOARD-pos-and-csu-health.md`](kql/fno/commerce/DASHBOARD-pos-and-csu-health.md) | POS / CSU / CRT — AppSession walk, Event ID 5000/5009, RetailServer latency |
| Tenant inventory (ARG) | [`kql/resourcegraph/DASHBOARD-tenant-inventory.md`](kql/resourcegraph/DASHBOARD-tenant-inventory.md) | Power Platform resources inventory — counts, owners, connectors. **Azure Resource Graph**, not App Insights. |

---

## See also

- [`README.md`](README.md) — repo entry point
- [`AGENTS.md`](AGENTS.md) — routing rules, layout, and editing conventions (read this before contributing or asking Copilot to extend the corpus)
- [`kql/README.md`](kql/README.md) — KQL index with provenance map
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — query style and PR rules
