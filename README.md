# Dynamics 365 / Power Platform · Application Insights KQL Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A curated, **vendor-neutral** collection of [Kusto (KQL)](https://learn.microsoft.com/azure/data-explorer/kusto/query/) queries for troubleshooting **Microsoft Dynamics 365 and Power Platform** workloads using [Azure Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview).

Covers **Dataverse, Model-Driven Apps, Power Pages, Canvas, Power Automate, Power Apps Mobile, Copilot Studio, and Dynamics 365 Finance & Supply Chain (F&O / FSCM)**.

Organized by component so you can find the right query in seconds, and designed to work well with **GitHub Copilot** for guided troubleshooting (see [AGENTS.md](AGENTS.md)).

## What's in here

```
kql/
├── _shared/                cross-component utilities (noise filters, channel split, all-table pulse)
├── dataverse/              Web API requests, SDK dependencies, plug-ins, server-side exceptions
├── modeldrivenapp/         UCI pageViews, form perf, web resources, Monitor tool exports
├── powerpages/             Portal pages, anon vs authenticated, page perf
├── canvasapp/              Canvas app sessions, slowest screens
├── powerautomate/          Cloud flow run / trigger / action failures
├── mobile/                 Power Apps Mobile offline sync diagnostics (Field Service Mobile)
├── fno/                    D365 Finance & Supply Chain — Batch, DMF, Errors, Forms, SlowQueries, Custom, Commerce
├── conversationdiagnostics/  Customer Service / Contact Center unified routing
├── platform-traces/        Generic `traces`-table TSG skeleton
└── resourcegraph/          Azure Resource Graph tenant inventory (NOT App Insights)
```

See [`kql/README.md`](kql/README.md) for the full index, per-folder READMEs for file lists, and the [provenance map](kql/README.md#provenance-map-source--component-folder) showing which upstream repo each query came from.

## Quick start

1. Clone this repo (or browse files on GitHub).
2. Open the [Azure portal](https://portal.azure.com) → **Application Insights** → your resource → **Logs**.
3. Open any `.kql` file in this repo, copy the contents, paste into the Logs query editor.
4. Substitute the placeholders (see [Placeholder convention](kql/README.md#placeholder-convention)).
5. Run.

Every `.kql` file is **standalone** — no project-wide setup, no `let` imports, no shared lambdas you have to paste in separately. The reusable noise-filter lambda from `_shared/exceptions/02-known-noise-filter.kql` is inlined into every consuming file.

## Use with GitHub Copilot + Akusto Explorer

The repo is designed to be driven from VS Code with two extensions: **Kusto** (a.k.a. "Akusto Explorer") for running queries inline, and **GitHub Copilot Chat** for guided troubleshooting.

**[Read the setup + usage guide → `GUIDE-USING-WITH-COPILOT.md`](GUIDE-USING-WITH-COPILOT.md)** — covers extension install, connecting Kusto to your App Insights resource, the two main Copilot workflows (regenerate a dashboard / walk through a symptom), and how to extend the corpus.

Then ask Copilot questions like:

> *"@workspace My users are seeing slow form loads on the case form. Use `kql/modeldrivenapp/DASHBOARD-uci-form-perf.md` to pick the right tiles in order."*
>
> *"@workspace Show me how to detect a sudden 5xx error spike during business hours using `kql/dataverse/`."*
>
> *"@workspace Regenerate `kql/conversationdiagnostics/DASHBOARD-conversation-routing.md` in my App Insights resource."*

Copilot follows the layout in [AGENTS.md](AGENTS.md) and the per-folder `DASHBOARD-*.md` files (see below) to pick the right `.kql` and walk you through it.

## Dashboards

Every folder under `kql/` ships at least one **`DASHBOARD-*.md`** — a self-contained markdown catalog of related queries with tile titles, visualisation types, source `.kql` links, and Copilot prompts to (re)generate or troubleshoot.

| Component | Dashboard | What it covers |
|---|---|---|
| Cross-component | [`kql/_shared/DASHBOARD-overview.md`](kql/_shared/DASHBOARD-overview.md) | First-look pulse, channel split, exception noise, ingestion cost |
| Dataverse | [`kql/dataverse/DASHBOARD-plugin-and-webapi-health.md`](kql/dataverse/DASHBOARD-plugin-and-webapi-health.md) | Plug-ins, Web API, SDK dependencies, server exceptions |
| Model-Driven Apps | [`kql/modeldrivenapp/DASHBOARD-uci-form-perf.md`](kql/modeldrivenapp/DASHBOARD-uci-form-perf.md) | UCI page loads, form perf, browser/device/geo, Monitor tool |
| Power Pages | [`kql/powerpages/DASHBOARD-portal-perf.md`](kql/powerpages/DASHBOARD-portal-perf.md) | Portal page perf, anonymous vs authenticated |
| Canvas Apps | [`kql/canvasapp/DASHBOARD-canvas-health.md`](kql/canvasapp/DASHBOARD-canvas-health.md) | Canvas sessions, slowest screens |
| Power Automate | [`kql/powerautomate/DASHBOARD-flow-runs.md`](kql/powerautomate/DASHBOARD-flow-runs.md) | Flow runs, action / trigger failures, billable-action leaderboards |
| Power Apps Mobile | [`kql/mobile/DASHBOARD-fs-mobile-offline.md`](kql/mobile/DASHBOARD-fs-mobile-offline.md) | Field Service Mobile offline sync — summary / errors / perf / payload / details |
| Conversation Diagnostics | [`kql/conversationdiagnostics/DASHBOARD-conversation-routing.md`](kql/conversationdiagnostics/DASHBOARD-conversation-routing.md) | Unified routing — fallback, overflow, CSR rejections, point-in-time rep state |
| F&O · Batch | [`kql/fno/batch/DASHBOARD-batch-monitoring.md`](kql/fno/batch/DASHBOARD-batch-monitoring.md) | Batch framework, threads, throttling, infolog errors, PBS queue |
| F&O · DMF | [`kql/fno/dmf/DASHBOARD-dmf-monitoring.md`](kql/fno/dmf/DASHBOARD-dmf-monitoring.md) | Data Management Framework imports / exports / errors |
| F&O · Errors | [`kql/fno/errors/DASHBOARD-errors-triage.md`](kql/fno/errors/DASHBOARD-errors-triage.md) | Exceptions by execution mode / legal entity / user |
| F&O · Forms | [`kql/fno/forms/DASHBOARD-form-perf.md`](kql/fno/forms/DASHBOARD-form-perf.md) | Form open frequency and duration |
| F&O · Slow SQL | [`kql/fno/slowqueries/DASHBOARD-slow-sql.md`](kql/fno/slowqueries/DASHBOARD-slow-sql.md) | AOS-surfaced slow queries |
| F&O · X++ Custom | [`kql/fno/custom/DASHBOARD-xpp-custom-signals.md`](kql/fno/custom/DASHBOARD-xpp-custom-signals.md) | X++ custom telemetry — UserLogOn, X++ exceptions, trace severity |
| Commerce | [`kql/fno/commerce/DASHBOARD-pos-and-csu-health.md`](kql/fno/commerce/DASHBOARD-pos-and-csu-health.md) | POS / CSU / CRT — AppSession walk, Event ID 5000 / 5009, RetailServer latency |
| Tenant inventory (ARG) | [`kql/resourcegraph/DASHBOARD-tenant-inventory.md`](kql/resourcegraph/DASHBOARD-tenant-inventory.md) | Power Platform resources inventory — counts, owners, connectors. **Azure Resource Graph**, not App Insights. |

## What is and isn't here

| ✅ Included | ❌ Not included |
|---|---|
| KQL for App Insights data emitted by Power Platform components | Bicep / ARM / Terraform for Application Insights provisioning |
| Markdown **`DASHBOARD-*.md`** catalogs per folder — paste into Copilot Chat to regenerate or walk through symptoms | Pre-built Azure Workbooks JSON / Grafana panels |
| Reusable noise-filter and anomaly-detection patterns | A configured App Insights resource (you bring your own) |
| Time-series, ranking, percentile, and anomaly queries | Customer-specific data — every query is generic |
| Azure Resource Graph tenant inventory queries | An LLM — you bring your own GitHub Copilot subscription |

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for query style, file-header format, and folder placement rules.

## Security

If you find a security issue (an unsanitized query that leaks sensitive data when run, an injection-style construct, etc.) please follow [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). Upstream queries are attributed via their `// Source:` headers and the [provenance map](kql/README.md#provenance-map-source--component-folder). Original repos retain their own licenses (mostly MIT / CC-BY).
