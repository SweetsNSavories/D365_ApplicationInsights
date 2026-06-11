# Dashboard — Customer Service / Contact Center conversation routing

> **For:** Customer Service supervisors, contact-center admins, unified-routing implementers.
> **Signal:** `traces` filtered to `customDimensions["powerplatform.analytics.scenario"] == "ConversationDiagnosticsScenario"`.
> **Window:** 1–7 d hot triage, 30 d for trends.
> **Pivot keys:** `customDimensions["powerplatform.analytics.resource.id"]` (conversation / work-item ID, a.k.a. `lwiid`; also reused as the **agent ID** on `AgentConfiguration` / `AgentStatusAndCapacity` rows), `customDimensions["powerplatform.analytics.subscenario"]` (stage discriminator — see [README](./README.md#subscenario-reference)).
> **Prerequisites:** [Configure conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/configure-conversation-diagnostics) enabled on the Customer Service / Contact Center environment, with telemetry flowing to your customer-owned Application Insights resource.

## What this dashboard tells you

Why a customer's conversation didn't get assigned, why a rep got bypassed, where overflow is firing, and what the state of every rep on a queue looked like at the moment of a specific routing decision.

This is the **App Insights** path for conversation routing diagnostics, not the deprecated Dataverse-side `msdyn_unifiedroutingdiagnostic` tables — see [`README.md`](./README.md#out-of-scope-for-this-folder).

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `<lwiid>` | 01, 04, 16, 17, 19 | `'00aaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'` | Conversation / work-item ID; this is the `powerplatform.analytics.resource.id` value on conversation rows |
| `<agentId>` | 10, 11, 13, 14 | `'00aaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'` | Representative ID — same field as `lwiid` but on `AgentConfiguration` / `AgentStatusAndCapacity` rows |
| `<queueId>` | 08, 12 | `'00aaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'` | Queue ID being targeted |
| `<pointInTime>` | 08, 09, 10, 11, 12, 13, 14 | `datetime(2026-06-10 15:00:00)` | The "as of" timestamp for point-in-time snapshots |
| `agentids` (dynamic array) | 09 | `dynamic(['<id1>','<id2>'])` | A shortlist of reps to compare |
| `ago(1d)` / `ago(7d)` / `ago(30d)` | every tile | `ago(7d)` | Override per tile |

## Tile plan

### Lifecycle & end-to-end

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 01 | Conversation lifecycle by ID | table | [`01-conversation-lifecycle-by-id.kql`](01-conversation-lifecycle-by-id.kql) | Replay every diagnostic event for one conversation chronologically — **start here** |
| 19 | End-to-end conversation tracing | table | [`19-end-to-end-conversation-tracing.kql`](19-end-to-end-conversation-tracing.kql) | Full event walk with `callId` + `channelType` projection |
| 04 | Conversation orchestration events | table | [`04-conversation-orchestration-events.kql`](04-conversation-orchestration-events.kql) | `AgCDDiagnosticsEvent` orchestrator decisions — `Rule` / `Scenario` / `Prompt` / `Action` / `Event` per stage |

### Routing failures

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 02 | Fallback queue conversations | table | [`02-fallback-queue-conversations.kql`](02-fallback-queue-conversations.kql) | Conversations whose `RouteToQueue` landed on the fallback queue — routing-rule misconfig signal |
| 03 | Overflow triggered conversations | table | [`03-overflow-triggered-conversations.kql`](03-overflow-triggered-conversations.kql) | Conversations where queue overflow was triggered (`OverflowTrigger`) |
| 18 | Conversations ended unsuccessfully | table | [`18-conversations-ended-unsuccessfully.kql`](18-conversations-ended-unsuccessfully.kql) | Voice calls with `CallEndDiagnosticEvent` + non-zero `CallStatusCode` |

### Assignment & rejections

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 05 | CSR rejections by conversation | table | [`05-csr-rejections-by-conversation.kql`](05-csr-rejections-by-conversation.kql) | Conversations rejected by >1 rep with per-agent rejection counts |
| 06 | Top 20 rejectors | barchart | [`06-csr-rejections-top20-agents.kql`](06-csr-rejections-top20-agents.kql) | Top 20 reps by total `CSRRejected` count |
| 07 | Assignment time > 2 min | table | [`07-assignment-time-over-2min.kql`](07-assignment-time-over-2min.kql) | Conversations where `CSRAccepted - latest RouteToQueue` > 2 min |
| 15 | Manual assignments tracked | table | [`15-manual-assignments-track.kql`](15-manual-assignments-track.kql) | `CSRAssignment` + `ManualAssignment` audit with `IsAgentAssigned` flag |

### Resource-intensive deep dives

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 08 | Why didn't this conversation get assigned? | table | [`08-why-conversation-not-assigned.kql`](08-why-conversation-not-assigned.kql) | **Resource-intensive.** State of every rep on the queue at the assignment timestamp |
| 09 | Why agent X and not agent Y? | table | [`09-why-agent-x-vs-agent-y.kql`](09-why-agent-x-vs-agent-y.kql) | **Resource-intensive.** Compare a shortlist of reps at the assignment timestamp |

> **Caveat for 08 / 09:** the 7-CTE shape can be slow over wide time windows. Tighten `<pointInTime>` to the minute, not the day.

### Point-in-time rep state

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 10 | Agent presence at point in time | table | [`10-agent-presence-at-point-in-time.kql`](10-agent-presence-at-point-in-time.kql) | One rep's presence (`Available` / `Busy` / …) |
| 11 | Agent unit capacity at point in time | table | [`11-agent-unit-capacity-at-point-in-time.kql`](11-agent-unit-capacity-at-point-in-time.kql) | One rep's unit-mode capacity |
| 12 | Agents in queue at point in time | table | [`12-agents-in-queue-at-point-in-time.kql`](12-agents-in-queue-at-point-in-time.kql) | All reps on one queue at the timestamp |
| 13 | Agent capacity profiles at point in time | table | [`13-agent-capacity-profiles-at-point-in-time.kql`](13-agent-capacity-profiles-at-point-in-time.kql) | One rep's capacity-profile breakdown |
| 14 | Agent skills at point in time | table | [`14-agent-skills-at-point-in-time.kql`](14-agent-skills-at-point-in-time.kql) | One rep's skills + skill ratings |

### Transfers, consults, audit

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| 16 | Transfers tracked by conversation | table | [`16-transfers-track-by-conversation.kql`](16-transfers-track-by-conversation.kql) | Transfer-attempt audit for one conversation |
| 17 | Consults tracked by conversation | table | [`17-consults-track-by-conversation.kql`](17-consults-track-by-conversation.kql) | Consult-attempt audit for one conversation |

## Flagship tile — paste & run

### Tile 01 · Conversation lifecycle by ID

**Viz:** table
**Source:** [`./01-conversation-lifecycle-by-id.kql`](./01-conversation-lifecycle-by-id.kql)

Always run this first when investigating a single bad conversation. Substitute the conversation/work-item ID into `<lwiid>` and read the events top-to-bottom. The shape of the event sequence — RouteToQueue → CSRAssignment → CSRRejected → CSRAssignment → CSRAccepted (or RouteToQueue → fallback) — tells you most of what you need before you touch any other tile.

### Tile 08 · Why didn't this conversation get assigned?

**Viz:** table
**Source:** [`./08-why-conversation-not-assigned.kql`](./08-why-conversation-not-assigned.kql)

The "rep state at the moment of decision" tile. Drill here after tile 01 shows a conversation hit `CSRRejected` repeatedly or landed on fallback. Each row is one rep on the queue at `<pointInTime>` with their presence, unit capacity, profile capacity, skills — so you can see exactly who was eligible and why the orchestrator picked (or didn't pick) them.

## Build in Azure Data Explorer dashboards

Two paths:

**Path A — import the pre-built dashboard.** Microsoft FastTrack ships an importable ADX dashboard JSON wiring the same tiles as this dashboard at [Dynamics-365-FastTrack-Implementation-Assets · `ConversationDiagnostics/`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets/tree/master/Customer%20Service/Customer%20Service/ComponentLibrary/AppInsights-Telemetry/ConversationDiagnostics). Download, **Azure Data Explorer dashboards → New → Import file**, point at your App Insights cluster URI.

**Path B — build from scratch.**

1. Create dashboard `Conversation routing diagnostics`.
2. Add your App Insights resource as a data source ([`../../GUIDE-USING-WITH-COPILOT.md`](../../GUIDE-USING-WITH-COPILOT.md)).
3. Five pages aligned to the tile plan sections: **Lifecycle**, **Routing failures**, **Assignment & rejections**, **Point-in-time state**, **Audit**.
4. For each tile, **+ Add tile** → paste the linked `.kql` → pick the **Viz** column value.
5. Expose `<lwiid>`, `<agentId>`, `<queueId>`, `<pointInTime>`, `agentids` as dashboard parameters.

## Build live dashboard with GitHub Copilot

Ask Copilot to run the linked KQL through the Kusto / Akusto Explorer extension, render the returned result or chart, and write observations from the rows. Do not stop at listing query files.

> *"@workspace Use [`DASHBOARD-conversation-routing.md`](./DASHBOARD-conversation-routing.md). Build a live dashboard for the **Routing failures** + **Assignment & rejections** pages (tiles 02, 03, 05, 06, 07, 15, 18) in my App Insights. Cluster URI `<...>`, database `<...>`."*

Symptom-driven (most common shape):

> *"@workspace A supervisor said conversation `<lwiid>` was rejected three times and ended up on the fallback queue. Use this dashboard — start with tile 01, then if rejections are real run tile 05, then tile 08 with the timestamp from tile 01's RouteToQueue event."*

Compare two reps:

> *"@workspace Conversation `<lwiid>` went to agent X but supervisor expected it to go to agent Y. Use tile 09 with `agentids = dynamic(['<X>','<Y>'])` and `<pointInTime>` from tile 01."*

## Related dashboards

- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — confirm `traces` are flowing and `ConversationDiagnosticsScenario` is the scenario name in your environment
- [`./README.md`](./README.md) — full subscenario reference + customDimensions schema (these are the field names every query parses)

## Reference

- [Sample queries and dashboards for conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/conversation-diagnostics-sample-queries) — verbatim source of the 19 KQL files
- [Subscenarios in conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/conversation-diagnostics-subscenarios)
- [Diagnose contact center health using Application Insights dashboard](https://learn.microsoft.com/en-us/dynamics365/contact-center/use/diagnose-dashboard) — supervisor-facing UI sitting on top of these queries
