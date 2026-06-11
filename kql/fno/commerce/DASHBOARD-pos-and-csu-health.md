# Dashboard — D365 Commerce (POS / CSU / CRT) health

> **For:** Commerce technical consultants, POS rollout owners, CSU / RetailServer ops.
> **Signals:** `customEvents` (POS extension events, CRT extension traces, async order processing), `requests` (CSU `Event ID 5000` incoming, `Event ID 5009` RetailServer API latency)
> **Window:** 1 d hot, 7 d trends
> **Pivot keys:** `customDimensions.AppSessionID` (POS app session), `customDimensions.UserSessionID` (cashier session), `cloud_RoleName` (Cloud POS / Modern POS / CSU / RetailServer)
> **Prerequisites:** Commerce telemetry export to App Insights from Cloud POS, Modern POS, CSU, and CRT extensions (see [Telemetry for D365 Commerce](https://learn.microsoft.com/en-us/dynamics365/commerce/dev-itpro/commerce-telemetry-instrumentation)).

## What this dashboard tells you

The cross-tier health of a D365 Commerce deployment — from POS terminal (Cloud POS / Modern POS) through CSU (Channel-Specific Unit, the regional gateway) to CRT (Commerce Runtime extensions). Six tiles cover the typical day-to-day triage: extension inventory, AppSession walk for a single terminal, the two flavors of RetailServer incoming/outgoing telemetry, and async order processing.

> **Event ID 5000 vs 5009:** Commerce CSU logs *two* high-volume telemetry shapes — `Event ID 5000` for inbound CSU requests, and `Event ID 5009` for RetailServer API latency. They look similar at a glance but answer different questions. Tile 04 covers 5000; tile 06 covers 5009. Don't confuse them.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `<AppSessionID>` | 03 | `'00aaaaaa-bbbb-…'` | Pull from a POS terminal's telemetry — same AppSessionID flows through every event of a session |
| `<extensionName>` | 01, 02 | `'Contoso.Commerce.POS.Extension'` | Optional filter to a specific extension assembly |
| `ago(1d)` / `ago(7d)` | every tile | `ago(1d)` | Override per tile |

## Tile catalog

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | POS extension events inventory | table | [`01-pos-extension-events-inventory.kql`](01-pos-extension-events-inventory.kql) | What custom POS extension events are flowing (names + frequency) |
| 02 | CRT extension traces inventory | table | [`02-crt-extension-traces-inventory.kql`](02-crt-extension-traces-inventory.kql) | What CRT extension traces are flowing (names + frequency) |
| 03 | Walk an AppSession end-to-end | table | [`03-walk-app-session.kql`](03-walk-app-session.kql) | All telemetry for one POS terminal session chronologically |
| 04 | CSU incoming requests — Event ID 5000 | table | [`04-csu-incoming-requests-event-5000.kql`](04-csu-incoming-requests-event-5000.kql) | Inbound CSU traffic with status / latency |
| 05 | Async order processing batches | table | [`05-async-order-processing-batches.kql`](05-async-order-processing-batches.kql) | Async-uploaded order batches from POS to HQ |
| 06 | RetailServer API latency — Event ID 5009 | table | [`06-retail-api-latency-event-5009.kql`](06-retail-api-latency-event-5009.kql) | RetailServer API call latency from CSU to HQ |

## Flagship tile — paste & run

### Tile 03 · Walk an AppSession end-to-end

**Viz:** table
**Source:** [`./03-walk-app-session.kql`](./03-walk-app-session.kql)

The single most useful tile when a cashier or store manager reports "the terminal froze at this time". Substitute the `<AppSessionID>` from the POS About page; the query returns every event the terminal emitted, in order — extension calls, CSU requests, async batches, exceptions.

### Tile 06 · RetailServer API latency — Event ID 5009

**Viz:** table
**Source:** [`./06-retail-api-latency-event-5009.kql`](./06-retail-api-latency-event-5009.kql)

The "is HQ the slow link?" tile. When tile 03 shows a POS session waiting on RetailServer calls, this aggregates by API operation to find which RetailServer endpoint is the bottleneck for the period.

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `D365 Commerce — POS & CSU health`.
2. Add your Commerce App Insights resource as a data source.
3. Two pages:
   - **Inventory & session walk** — 01, 02, 03
   - **CSU / RetailServer / Async** — 04, 05, 06
4. Expose `_startTime`, `_endTime`, `<AppSessionID>` as dashboard parameters.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-pos-and-csu-health.md`](./DASHBOARD-pos-and-csu-health.md). Regenerate all 6 tiles in my Commerce App Insights — cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace A cashier in Store 42 said the POS hung at 14:13 local. AppSessionID is `<...>`. Use tile 03 to walk the session, then if I see slow CSU calls there, use tile 04 (Event 5000) to confirm CSU side, and tile 06 (Event 5009) to drill RetailServer latency."*

## Related dashboards

- [`../batch/DASHBOARD-batch-monitoring.md`](../batch/DASHBOARD-batch-monitoring.md) — async order processing (tile 05) runs on the F&O batch framework
- [`../errors/DASHBOARD-errors-triage.md`](../errors/DASHBOARD-errors-triage.md) — F&O exception triage that includes Commerce surfaces
- [`../custom/DASHBOARD-xpp-custom-signals.md`](../custom/DASHBOARD-xpp-custom-signals.md) — X++ custom telemetry (UserLogOn, exceptions) including Commerce-emitted traces
