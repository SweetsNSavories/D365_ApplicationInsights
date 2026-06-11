# `_shared/cost/` — Ingestion cost & noise queries

Cross-component queries to keep your App Insights bill under control. Derived from
the Microsoft guidance in
[Understand and control costs (F&O)](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/monitoring-telemetry/monitoring-understanding-and-controlling-cost)
and the Azure Monitor articles it links to.

| File | What it shows |
|---|---|
| [`01-ingestion-volume-by-table-30d.kql`](01-ingestion-volume-by-table-30d.kql) | Daily billable ingestion (GB) per table over 30 d, stacked column chart. The starting point for any cost investigation — reveals which stream (`traces`, `customEvents`, `requests`, etc.) is the spender. |
| [`02-noisy-signals-candidates-for-sampling.kql`](02-noisy-signals-candidates-for-sampling.kql) | Top 25 noisiest `customEvents.name` values and top 25 noisiest `traces.message` shapes (truncated to 200 chars) over 7 d, with `Rows`, `PctOfTable`, and `Users`. Signals > 10 % of their table are strong sampling / suppression candidates. |

## When to use

- Bill came in higher than expected — start with `01` to see which table spiked.
- Onboarding a new F&O environment — run both before turning on every signal.
- After enabling a new custom signal (see [`../../fno/custom/`](../../fno/custom/README.md)) — re-run `02` to confirm it's not dwarfing the rest.

## Cost levers (from the upstream docs)

1. **Sampling** (adaptive or fixed-rate) — preserves statistical accuracy at lower volume.
2. **Daily cap** — prevents runaway cost but causes data loss when hit.
3. **Workspace-based resources** — unlocks Basic Logs and commitment-tier pricing.
4. **Retention** — keep hot tier short, archive older data.
5. **Selective telemetry** — turn off signals you aren't acting on. Use `01` to identify them.

## Notes

- Both queries use the `Usage` (table-level billable counters) and standard
  AppInsights tables. They require a workspace-based App Insights resource
  (the default since 2021); classic-only resources don't expose `Usage`.
- `Usage.Quantity` is in MB — the GB conversion is `/ 1024.0`.
