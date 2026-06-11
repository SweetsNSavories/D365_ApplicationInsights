# _shared/exceptions/

Reusable noise filtering for the App Insights `exceptions` table. The core idea: in a Dataverse-backed environment, **>50 %** of `exceptions` rows are `PrvRead` / `PrincipalPrivilegeDenied` on first-party (`msdyn*`, `adx_*`, `mscrm_*`) entities — these are baseline noise from speculative reads during navigation, not real errors. You must classify and remove them before any exception trend is meaningful.

## Files

| # | File | What it does |
|---|---|---|
| 01 | [`01-noise-catalog-breakdown-7d.kql`](01-noise-catalog-breakdown-7d.kql) | What noise classes exist in YOUR env (7-day catalog) |
| 02 | [`02-known-noise-filter.kql`](02-known-noise-filter.kql) | **The reusable `_IsNoise` lambda** — copy/paste into any exception query |
| 03 | [`03-top10-real-problems-7d.kql`](03-top10-real-problems-7d.kql) | Top 10 exceptions **excluding** noise — the actionable list |
| 04 | [`04-exceptions-signal-vs-noise-30d.kql`](04-exceptions-signal-vs-noise-30d.kql) | Daily timeline: noise vs signal stacked, 30 d |
| 05 | [`05-noise-self-check-7d.kql`](05-noise-self-check-7d.kql) | Sanity check: % classified as noise (should be high) |
| 06 | [`06-noise-discovery-candidates-7d.kql`](06-noise-discovery-candidates-7d.kql) | Find *new* noise patterns to add to the lambda |
| 07 | [`07-firstparty-prefix-breakdown-7d.kql`](07-firstparty-prefix-breakdown-7d.kql) | Which first-party prefixes dominate the noise |

## The lambda (verbatim, from 02-known-noise-filter.kql)

```kql
let _IsNoise = (msg:string, ent:string) {
       (msg has "PrvRead" or msg has "prvRead" or msg has "0x80040220")
    or  msg has "SecLib::"
    or  msg has "PrincipalPrivilegeDenied"
    or ((ent startswith "msdyn"     or ent startswith "adx_"
      or ent startswith "msdyncrm_" or ent startswith "msdyn365_"
      or ent startswith "mscrm_")
        and (msg has "Principal"   or msg has "privilege"
          or msg has "Access"      or msg has "denied"))
    or  msg has "was cancelled"
    or  msg has "OperationCanceled"
    or  msg has "TooManyRequests"
};
```

Run **06** periodically — if a new high-volume pattern shows up that isn't yet in the lambda, add it and bump the file.
