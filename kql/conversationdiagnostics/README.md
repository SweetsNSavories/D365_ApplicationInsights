# `kql/conversationdiagnostics/` — Customer Service / Contact Center conversation diagnostics

Diagnostic traces emitted by **Dynamics 365 Customer Service** and **Dynamics 365 Contact Center** unified routing when [Conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/configure-conversation-diagnostics) is enabled. Telemetry flows to your customer-owned Application Insights resource via the `traces` table.

## What's covered

Every query here targets the `traces` table and filters on `customDimensions["powerplatform.analytics.scenario"] == "ConversationDiagnosticsScenario"` (the canonical scenario name). The **subscenario** field is the discriminator — see the subscenario reference below.

| File | Purpose |
|---|---|
| [01-conversation-lifecycle-by-id.kql](01-conversation-lifecycle-by-id.kql) | Replay every diagnostic event for one conversation in chronological order. Start here. |
| [02-fallback-queue-conversations.kql](02-fallback-queue-conversations.kql) | Conversations whose `RouteToQueue` landed on the fallback queue (rule misconfig signal) |
| [03-overflow-triggered-conversations.kql](03-overflow-triggered-conversations.kql) | Conversations where queue overflow was triggered (`OverflowTrigger` keyword) |
| [04-conversation-orchestration-events.kql](04-conversation-orchestration-events.kql) | `AgCDDiagnosticsEvent` rows — orchestrator `Rule` / `Scenario` / `Prompt` / `Action` / `Event` per decision |
| [05-csr-rejections-by-conversation.kql](05-csr-rejections-by-conversation.kql) | Conversations rejected by more than one representative, with per-agent rejection counts |
| [06-csr-rejections-top20-agents.kql](06-csr-rejections-top20-agents.kql) | Top 20 representatives by total `CSRRejected` count |
| [07-assignment-time-over-2min.kql](07-assignment-time-over-2min.kql) | Conversations where `CSRAccepted - latest RouteToQueue` > 2 min |
| [08-why-conversation-not-assigned.kql](08-why-conversation-not-assigned.kql) | **Resource-intensive.** State of every rep on the queue at a given assignment timestamp |
| [09-why-agent-x-vs-agent-y.kql](09-why-agent-x-vs-agent-y.kql) | **Resource-intensive.** Compare a shortlist of reps at a given assignment timestamp |
| [10-agent-presence-at-point-in-time.kql](10-agent-presence-at-point-in-time.kql) | One-representative point-in-time presence |
| [11-agent-unit-capacity-at-point-in-time.kql](11-agent-unit-capacity-at-point-in-time.kql) | One-representative point-in-time unit-mode capacity |
| [12-agents-in-queue-at-point-in-time.kql](12-agents-in-queue-at-point-in-time.kql) | All representatives on a queue at a given timestamp |
| [13-agent-capacity-profiles-at-point-in-time.kql](13-agent-capacity-profiles-at-point-in-time.kql) | One-representative point-in-time capacity-profile breakdown |
| [14-agent-skills-at-point-in-time.kql](14-agent-skills-at-point-in-time.kql) | One-representative point-in-time skills + skill ratings |
| [15-manual-assignments-track.kql](15-manual-assignments-track.kql) | `CSRAssignment` + `ManualAssignment` audit with `IsAgentAssigned` flag |
| [16-transfers-track-by-conversation.kql](16-transfers-track-by-conversation.kql) | Transfer-attempt audit (events for one conversation, ordered) |
| [17-consults-track-by-conversation.kql](17-consults-track-by-conversation.kql) | Consult-attempt audit (events for one conversation, ordered) |
| [18-conversations-ended-unsuccessfully.kql](18-conversations-ended-unsuccessfully.kql) | Voice calls with `CallEndDiagnosticEvent` + non-zero `CallStatusCode` |
| [19-end-to-end-conversation-tracing.kql](19-end-to-end-conversation-tracing.kql) | Full event walk for one conversation with `callId` + `channelType` projection |

## customDimensions schema

The conversation-diagnostics signal lives in `customDimensions` on the `traces` table. The canonical keys (preserve casing exactly — they're embedded in `parse_json` paths inside every query):

| Key | Meaning |
|---|---|
| `powerplatform.analytics.scenario` | Always `"ConversationDiagnosticsScenario"` — the top-level scenario filter |
| `powerplatform.analytics.subscenario` | Stage discriminator — see subscenario table below |
| `powerplatform.analytics.resource.id` | Conversation / work-item ID (a.k.a. `lwiid`) — also reused as the **representative ID** on `AgentConfiguration` / `AgentStatusAndCapacity` rows |
| `powerplatform.analytics.resource.organization.id` | Tenant / organization ID |
| `type` | Event-type discriminator. Values seen: `"AgCDDiagnosticsEvent"` (orchestration), `"CallEndDiagnosticEvent"` (voice call end) |
| `omnichannel.target_agent.id` | Representative ID being targeted (on `CSRRejected`, `CSRAccepted`) |
| `omnichannel.initiator_agent.id` | Representative ID initiating an action |
| `omnichannel.target_queue.id` | Queue ID being targeted |
| `omnichannel.queue.ids` | All queue IDs the representative belongs to (JSON array as string) |
| `omnichannel.capacity_profile.ids` | Capacity profile IDs the representative holds (JSON array as string) |
| `omnichannel.capacity_profile` | Per-profile snapshot — JSON with `CapacityProfileId`, `AvailableCapacity`, `DefaultMaxCapacity` |
| `omnichannel.current_base_presence` | Presence string (`"Available"`, `"Busy"`, etc.) |
| `omnichannel.current_presence_id` | Presence ID |
| `omnichannel.available_capacity.units` | Unit-mode available capacity number |
| `omnichannel.associated_skills` | JSON array of `{CharacteristicId, RatingValue, SkillType, RatingModelMin, RatingModelMax}` |
| `omnichannel.result` | Stage result — JSON, e.g. `{DisplayName: "Fallback queue"}` on RouteToQueue |
| `omnichannel.additional_info` | Free-form per-event payload — JSON. Carries `Rule`, `Scenario`, `Prompt`, `OverflowTrigger`, etc. |
| `omnichannel.description` | Event description text |
| `omnichannel.action` | Action taken |
| `omnichannel.event` | Event name |
| `omnichannel.data` | Catch-all data bag — used by `AgentNameConfig` to map agentId → display name |
| `omnichannel.channel.type` / `ChannelType` | Channel discriminator (voice / chat / etc.). Both spellings exist in historical data — every query coalesces them. |
| `omnichannel.call.id` | Voice call ID |
| `omnichannel.assignment.status` | JSON with `IsAgentAssigned` flag (manual / automated assignment outcomes) |
| `CallStatusCode` | Voice-call exit code. Non-zero = unsuccessful. |

## Subscenario reference

The `powerplatform.analytics.subscenario` field identifies the routing stage. Full list documented at [Subscenarios in conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/conversation-diagnostics-subscenarios) — the ones the queries here filter on:

| Subscenario | Stage |
|---|---|
| `RouteToQueue` | Work item being routed to a queue (rule evaluation) |
| `CSRAssignment` | Automated assignment attempt to a representative |
| `ManualAssignment` | Manual / supervisor-driven assignment |
| `CSRAccepted` | Representative accepted the assignment |
| `CSRRejected` | Representative rejected the assignment |
| `AgentConfiguration` / `CSRConfigurationDetails` | Snapshot of one rep's queues + capacity profiles |
| `AgentStatusAndCapacity` / `CSRStatusandCapacityDetails` | Snapshot of one rep's presence + per-profile / unit capacity |
| `AgentNameConfig` | Maps agentId → display name (lookup table) |

Newer environments emit the `CSR*` naming (`CSRConfigurationDetails`, `CSRStatusandCapacityDetails`); older ones emit `Agent*`. Every query here filters on both.

## Out of scope for this folder

- **Unified routing diagnostics** (the Dataverse-side feature — `msdyn_unifiedroutingdiagnostic` / `msdyn_unifiedroutingrun` tables, [reference](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/unified-routing-diagnostics)) is being deprecated in favor of the App Insights path covered here. Those tables are queried via the Dataverse Web API, not KQL.
- **Copilot Studio** bot / agent traces — pending instrumentation reference. When data lands, add a sibling subfolder.
- **Conversation intelligence** (call recordings, transcripts, sentiment) is stored in dedicated storage accounts, not App Insights.

## Sources

- Verbatim KQL: [Sample queries and dashboards for conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/guidance/resources/conversation-diagnostics-sample-queries) (Microsoft Learn)
- Schema reference: [Subscenarios in conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/conversation-diagnostics-subscenarios)
- Setup: [Configure conversation diagnostics](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/configure-conversation-diagnostics)
- Supervisor UI: [Diagnose contact center health using Application Insights dashboard](https://learn.microsoft.com/en-us/dynamics365/contact-center/use/diagnose-dashboard)
- Importable Azure Data Explorer dashboard (same queries pre-wired): [Dynamics-365-FastTrack-Implementation-Assets · `ConversationDiagnostics/`](https://github.com/microsoft/Dynamics-365-FastTrack-Implementation-Assets/tree/master/Customer%20Service/Customer%20Service/ComponentLibrary/AppInsights-Telemetry/ConversationDiagnostics)
