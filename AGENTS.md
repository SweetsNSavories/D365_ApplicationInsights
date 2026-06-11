# AGENTS.md — guidance for GitHub Copilot and other coding agents

This repo is a **library of standalone KQL queries** for troubleshooting Microsoft Dynamics 365 and Power Platform workloads using Azure Application Insights. The core artifact is still paste-and-run `.kql`, with Markdown runbooks plus optional Python/Jupyter live-dashboard tooling that executes generated manifests and writes local customer-specific output.

## How to help the user

When the user opens this repo and asks for help troubleshooting:

1. **Identify the component** they're asking about. Pick the matching folder under `kql/`:
   - "Dataverse Web API / plug-in / server-side" → `kql/dataverse/`
   - "Model-driven app / UCI / form perf" → `kql/modeldrivenapp/`
   - "Power Pages portal / public site" → `kql/powerpages/`
   - "Canvas app" → `kql/canvasapp/`
   - "Cloud flow / Power Automate" → `kql/powerautomate/`
   - "Power Apps Mobile / offline sync" → `kql/mobile/`
   - "Dynamics 365 Finance & Supply Chain / F&O / FSCM / AOS / batch jobs / DMF imports / X++ slow SQL / form perf in F&O" → `kql/fno/` (subfolders: `batch/`, `dmf/`, `errors/`, `forms/`, `slowqueries/`, `custom/`, `commerce/`)
   - "Dynamics 365 Commerce / POS / Cloud POS / Modern POS / CSU / RetailServer / CRT extension / AppSessionID / UserSessionID / Event ID 5000" → `kql/fno/commerce/`
   - "App Insights bill / ingestion cost / noisy signal / sampling candidates" → `kql/_shared/cost/` (applies across all components)
   - "Customer Service / Contact Center conversation diagnostics / unified routing / CSR not assigned / fallback queue / overflow / agent rejected / assignment took too long" → `kql/conversationdiagnostics/` (uses `traces` table + `powerplatform.analytics.scenario == "ConversationDiagnosticsScenario"`)
   - "Copilot Studio bot / agent" → not yet covered; instrumentation reference still pending
   - Cross-component (e.g. "portal vs MDA pageViews") → `kql/_shared/`
   - Tenant inventory (e.g. "list all flows", "find an agent") → `kql/resourcegraph/` (note: different runtime — **Azure Resource Graph**, not App Insights)
2. **Time-series / daily / 30d / anomaly questions** → look in the `timelines/` subfolder of the matching component, or `_shared/timelines/`.
3. **Exception trend questions** → ALWAYS apply the noise filter first. The reusable lambda is in `kql/_shared/exceptions/02-known-noise-filter.kql` and is **inlined** into `03-top10-real-problems-7d.kql`, `04-exceptions-signal-vs-noise-30d.kql`, etc. Without the filter, ~80% of exception rows on a Dataverse-backed env are `PrvRead` / `PrincipalPrivilegeDenied` noise on first-party (`msdyn*`, `adx_*`, `mscrm_*`) entities.
4. **`pageViews` channel disambiguation** — `pageViews` is shared by Model-Driven Apps AND Power Pages. The discriminator is:
   - `customDimensions.PortalId` populated → Power Pages
   - `customDimensions.appModule` populated → Model-Driven App
   - neither → Other (canvas / custom JS SDK)
   See `kql/_shared/timelines/01-pageviews-daily-30d-by-channel.kql` for the canonical split.
5. **Correlation walks** — to follow one user action across tables, use `operation_Id`. Walk parent/child spans with `operation_ParentId` / `id`. UCI sessions are `session_Id`. See `kql/_shared/overview/02-pageviews-by-operation-id.kql`.
6. **F&O (`fno/`) specifics** — F&O telemetry is point-to-point to a customer-owned App Insights, distinct from the tenant-wide Power Platform pipeline. Triage facets to always include: `cloud_RoleName` (`AOSService` / `BatchService` / `DIXFService`), `cloud_RoleInstance` (the specific AOS), `customDimensions.ExecutionMode` (Interactive / Batch / Service / DMF), `customDimensions.LegalEntity`, `customDimensions.environmentId`. Dashboard parameters in every `fno/` file are `let` bindings near the top with safe defaults — empty string is the pass-through value because upstream queries use the `isempty(<var>) or <Column> == <var>` idiom.
7. **Live dashboard requests** → prefer the matching folder's `LIVE-DASHBOARD.ipynb` or `LIVE-DASHBOARD.json` when the user wants executable dashboards, results, observations, or CSV/HTML output. Each folder has a committed dry-run `live-output/index.html` preview. Use `tools/live_dashboard_runner.py`; write real customer runs to `live-dashboard-output/` or `cases/`, not the committed preview folder.

## Placeholder convention

When showing a query to the user, point out any placeholders that need substituting before running:

| Looks like | Means |
|---|---|
| `[userId]`, `[sessionIdHere]`, `[Plugin name here]` | Customer-supplied value |
| `<URLHere>` | Customer-supplied value (alt notation) |
| `00aa00aa-bb11-cc22-dd33-44ee44ee44ee` | Obvious-fake GUID — substitute with a real one |
| `// Replace …` | Inline instruction immediately above the literal to swap |

## Editing rules

- **Preserve every `.kql` file's `// Source:` header verbatim.** It points at the original repo / doc.
- **Inline shared lambdas — don't reference across files.** A user pasting one `.kql` into the Logs blade must not need a second file.
- **Naming**: lowercase-with-dashes, `NN-short-description.kql`, two-digit numeric prefix per folder.
- **New cross-component queries** → `kql/_shared/timelines/` (or `_shared/exceptions/`, etc.).
- **New component-specific queries** → bump the numeric prefix in that folder; update the folder's `README.md` table.
- **Resource Graph** queries always go in `kql/resourcegraph/` — they don't run in App Insights and shouldn't be `union`-ed with App Insights tables.
- **Do not commit customer-specific identifiers** (subscription GUIDs, resource names, real user IDs). Use the placeholder convention above.
- **Do not commit customer telemetry output**. Only dry-run `live-output/index.html` preview pages are committed. `live-output/observations.md`, `live-output/results.json`, `live-output/csv/`, `live-dashboard-output/`, and `cases/` must stay out of commits.

## What NOT to suggest

- Don't propose adding provisioning/application code (Bicep, ARM, Terraform, app samples) — this is a query library with live-dashboard runner tooling only. Direct the user to upstream Microsoft docs for provisioning.
- Don't propose Workbooks JSON or Grafana dashboards — out of scope.
- Don't propose creating new top-level component folders without first checking whether `_shared/` is the right home.
- Don't strip `// Source:` headers when refactoring.

## Repository layout (authoritative)

```
.
├── README.md                  user-facing entry point
├── AGENTS.md                  this file (Copilot guidance)
├── CONTRIBUTING.md            query style + PR rules
├── SECURITY.md                vulnerability reporting
├── LICENSE                    MIT
├── LIVE-DASHBOARDS.md         live dashboard runner workflow
├── requirements-live-dashboard.txt
├── tools/                     manifest generator, runner, validator
├── aliyoussefi-kql-extracted.md   raw extraction notes (history)
└── kql/                       all queries; see kql/README.md
    ├── README.md
    ├── _shared/{exceptions,overview,timelines,cost}/
    ├── dataverse/             + timelines/
    ├── modeldrivenapp/        + timelines/
    ├── powerpages/            + timelines/
    ├── canvasapp/
    ├── powerautomate/         + timelines/
    ├── mobile/
    ├── fno/                   D365 Finance & Supply Chain (F&O / FSCM)
    │   ├── batch/             batch framework, threads, throttling, PBS queue
    │   ├── dmf/               Data Management Framework (imports/exports)
    │   ├── errors/            exceptions triage by ExecutionMode/LegalEntity
    │   ├── forms/             form open frequency + perf via pageViews
    │   ├── slowqueries/       AOS-surfaced slow SQL
    │   ├── custom/            X++ custom telemetry signals (SysApplicationInsightsTelemetryLogger)
    │   └── commerce/          POS / Cloud POS / CSU / CRT extensions, AppSession walk, Event 5000
      ├── conversationdiagnostics/   Customer Service / Contact Center unified routing — fallback queues, CSR assignment, overflow, transfers, consults, point-in-time rep state
      ├── platform-traces/
      └── resourcegraph/
```

Every folder with runnable tiles also has generated `LIVE-DASHBOARD.json`, `LIVE-DASHBOARD.ipynb`, and dry-run `live-output/index.html` files. These are committed; generated customer outputs are not.
