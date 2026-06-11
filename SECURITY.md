# Security Policy

## Supported scope

This repository contains **read-only KQL queries** for Azure Application Insights. The queries themselves do not modify, ingest, or transmit data — they only return rows from telemetry tables you already own.

That said, security-relevant issues we care about:

- A query that, when run, **inadvertently surfaces sensitive data** (raw credentials, PII, secrets stored in `customDimensions`, etc.) without warning the user.
- A query that uses an **unsafe pattern** (e.g. unparameterized string concatenation that could be exploited if templated into another system).
- A `.kql` file that contains **leaked customer-identifying values** (real subscription IDs, resource names, user GUIDs, tenant IDs, URLs).
- Bad advice in a README or `AGENTS.md` that would lead a downstream user to grant excessive permissions or run a destructive command.

## Reporting

Please open a **private** advisory via the GitHub repo's **Security → Report a vulnerability** flow rather than a public issue.

If that isn't available for this fork/mirror, file an issue **without** the sensitive details and ask a maintainer to contact you privately.

## What to include

- The specific file path and line range.
- A short description of the risk.
- (If applicable) a suggested fix or sanitization.

## Response

We'll triage privately, acknowledge within a reasonable window, and credit you in the fix commit unless you'd prefer to stay anonymous.

## Out of scope

- Vulnerabilities in Azure Monitor / Application Insights / Kusto themselves — report those to [Microsoft Security Response Center](https://www.microsoft.com/msrc).
- Vulnerabilities in the upstream repos this library reproduces queries from — report those to the upstream maintainers; we'll happily update the inlined copy once they ship a fix.
