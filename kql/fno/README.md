# `kql/fno/` — Dynamics 365 Finance & Supply Chain Management (F&O / FSCM)

KQL for the **Finance & Operations** product family — Finance, Supply Chain, Commerce, HR, Project Operations — running on the AOS/X++ stack. Distinct from Dataverse-backed apps (Sales/Service/MDA/Power Pages) which live under sibling folders.

## How F&O telemetry reaches App Insights

F&O does **not** share a tenant-wide Power Platform telemetry pipeline. Each environment is configured with **point-to-point export to a customer-owned App Insights resource**. The schema lands in standard App Insights tables (`requests`, `dependencies`, `pageViews`, `exceptions`, `customEvents`, `traces`) but the **emitter** is the AOS / Batch / DIXF processes — discoverable via `cloud_RoleName`:

| `cloud_RoleName` | Emitter |
|---|---|
| `AOSService` | Online AOS (interactive web requests, X++ runtime, form rendering) |
| `BatchService` | Batch framework runner |
| `DIXFService` | Data Import/Export Framework worker |
| `Web` | Front-end (Forms client) |

Onboarding: [Monitoring and telemetry with Application Insights (Microsoft Learn)](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/monitoring-and-telemetry-appinsights).

## Layout

| Subfolder | What it covers |
|---|---|
| [`batch/`](batch/)             | Batch framework — server config, threads, throttling, priority, infolog errors, PBS queue |
| [`dmf/`](dmf/)                 | Data Management Framework — imports, exports, per-entity counts, staging vs target errors |
| [`errors/`](errors/)           | Top-down `exceptions` triage by execution mode, legal entity, user, message |
| [`forms/`](forms/)             | Form open frequency + perf via `pageViews` |
| [`slowqueries/`](slowqueries/) | SQL slow-query telemetry surfaced by AOS, for X++ / index tuning |
| [`custom/`](custom/)           | X++ custom telemetry signals (`SysApplicationInsightsTelemetryLogger`) — event inventory, user logons, X++ exceptions by `ClassName`/`MethodName`, traces by severity, custom metrics, DMF error reconciliation |
| [`commerce/`](commerce/)       | Commerce tier — POS / Cloud POS / CSU / CRT extensions; POS→CSU correlation via `AppSessionID` / `UserSessionID` / `ActivityID` (Event ID 5000); async customer-order batch classes |

## Cross-cutting reminders

- **`exceptions.customDimensions.ExecutionMode`** is the primary triage facet — `"Interactive"`, `"Batch"`, `"Service"`, `"DMF"`. Always include in groupings.
- **`cloud_RoleInstance`** identifies the specific AOS instance — useful when one AOS is misbehaving.
- **`customDimensions.LegalEntity`** is the X++ company code (DAT, USMF, etc.) and lets you split usage by org unit.
- **`customDimensions.environmentId`** scopes the F&O environment GUID — important when one App Insights resource is shared across multiple sandbox/UAT/prod environments.
- **`pageViews`** in F&O ≠ pageviews in MDA or Power Pages. Disambiguate via `cloud_RoleName` if you share App Insights across products. See [../_shared/timelines/01-pageviews-daily-30d-by-channel.kql](../_shared/timelines/01-pageviews-daily-30d-by-channel.kql).
- **Dashboard parameters** like `_startTime`, `_endTime`, `_environmentId`, `entityName`, `dataProject`, `_userId` appear at the top of every file as `let` bindings with safe defaults (`ago(7d)`, `now()`, `""`). Empty string is the pass-through value — the upstream queries all use the `isempty(<var>) or <Column> == <var>` idiom.

## Source / licensing

The `batch/`, `dmf/`, `errors/`, `forms/`, and `slowqueries/` `.kql` files were extracted from
[microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples](https://github.com/microsoft/Dynamics-365-FastTrack-FSCM-Telemetry-Samples) (MIT-licensed Microsoft sample repo). Each file carries an upstream `// Source:` header pointing back at the original dashboard JSON or `.kql`.

The `custom/` `.kql` files were authored locally, derived from the documented signal shapes in [Add custom telemetry signals (Microsoft Learn)](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-developer-add-custom-signals) and [Available telemetry (Microsoft Learn)](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-available-telemetry).

The `commerce/` `.kql` files were authored locally, derived from the documented signal shapes in [Log extension events to Application Insights (Commerce)](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/commerce-application-insights) and [Commerce component events for diagnostics and troubleshooting](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/retail-component-events-diagnostics-troubleshooting).

For ingestion-cost queries that apply across all components see [`../_shared/cost/`](../_shared/cost/README.md).

The upstream repo also ships an **X++ telemetry-extension sample** (under `DeveloperSamples/` and `SampleXppExtensions/`) — that's instrumentation source, not queries, and is intentionally **not** mirrored here. Refer to the upstream repo directly if you want to extend the F&O telemetry surface.
