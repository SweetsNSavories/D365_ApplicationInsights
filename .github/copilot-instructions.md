# GitHub Copilot — repository instructions

This repository is a **library of standalone Kusto (KQL) queries** for troubleshooting Microsoft Dynamics 365 and Power Platform workloads via Azure Application Insights. The primary artifacts are paste-and-run `.kql` files and Markdown runbooks, with optional Python/Jupyter tooling for generated live dashboards.

When the user asks for help, follow the routing and editing rules in [`AGENTS.md`](../AGENTS.md). Key shortcuts:

- Component-first layout under `kql/<component>/`. Cross-component utilities live in `kql/_shared/`. Resource Graph queries (different runtime) live in `kql/resourcegraph/`.
- For executable dashboard requests, use the folder's `LIVE-DASHBOARD.json` / `LIVE-DASHBOARD.ipynb` and `tools/live_dashboard_runner.py`. Do not commit generated `live-output/` folders.
- Every `.kql` is standalone — do not split a query across multiple files.
- Exception trend questions: always apply the noise filter (`kql/_shared/exceptions/02-known-noise-filter.kql`); it's already inlined into the consuming files.
- `pageViews` is split between Model-Driven Apps and Power Pages — disambiguate via `customDimensions.appModule` vs `customDimensions.PortalId`.
- Preserve the `// Source:` header on every `.kql`.
- Use the placeholder convention (`[likeThis]`, `<likeThis>`, obvious-fake GUIDs) — never commit real customer identifiers.

For the full layout and routing rules see [`AGENTS.md`](../AGENTS.md). For per-folder file lists, see each folder's `README.md`.
