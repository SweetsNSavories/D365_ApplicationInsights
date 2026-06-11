# Dashboard — Power Pages portal performance

> **For:** Power Pages makers, portal admins, site reliability owners.
> **Signals:** `pageViews` (portal page loads), `dependencies` (CMS / `_api/cms/...`), `exceptions` (server-side portal errors), `requests` (server-rendered pages)
> **Window:** 7 d hourly + 30 d daily
> **Pivot keys:** `customDimensions.PortalId`, `name` (page path), `user_AuthenticatedId` (anon vs authenticated), `client_City`
> **Prerequisites:** App Insights integration enabled for the Power Pages site ([onboarding](https://learn.microsoft.com/en-us/power-pages/admin/azure-application-insights)).

## What this dashboard tells you

Page load latency per route on your portal, anonymous vs authenticated split (where available), and the slowest pages over the last 7 days.

> **Channel disambiguator:** every tile here implicitly filters `customDimensions.PortalId` is populated. If `customDimensions.appModule` is populated → that's MDA → see [`../modeldrivenapp/DASHBOARD-uci-form-perf.md`](../modeldrivenapp/DASHBOARD-uci-form-perf.md). See [`../_shared/timelines/01-pageviews-daily-30d-by-channel.kql`](../_shared/timelines/01-pageviews-daily-30d-by-channel.kql) for the canonical split.

## Parameters

| Token | Where used | Example | Notes |
|---|---|---|---|
| `<PortalId>` | (when adding multi-portal filters) | `'01aaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'` | Pull from `customDimensions.PortalId` on a sample row |
| `ago(7d)` / `ago(30d)` | every tile | `ago(7d)` | Override per tile |

## Tile catalog

| # | Title | Viz | Source file | What it answers |
|---|---|---|---|---|
| timelines/01 | Top 10 slowest portal pages — hourly P95 (7 d) | timechart | [`timelines/01-portal-top-slow-pages-hourly-7d.kql`](timelines/01-portal-top-slow-pages-hourly-7d.kql) | Which pages are slowest, hour by hour, last 7 days |

## Recommended additions (not yet in repo)

These tiles round out a portal-perf dashboard; drop new `.kql` files here as you write them and update this catalog:

| Title (suggested) | Viz | KQL skeleton |
|---|---|---|
| pageViews daily by PortalId | columnchart | `pageViews | where isnotempty(customDimensions.PortalId) | summarize count() by bin(timestamp, 1d), tostring(customDimensions.PortalId)` |
| Anonymous vs authenticated daily | timechart | `pageViews | where isnotempty(customDimensions.PortalId) | extend isAuth = isnotempty(user_AuthenticatedId) | summarize count() by bin(timestamp, 1d), isAuth` |
| Top 10 server-side paths | barchart | `dependencies | where target endswith 'powerappsportals.com' or name has '/_api/cms/' | summarize count(), avg(duration), percentile(duration, 95) by name | top 10 by count_` |
| Form-submission failures | table | `dependencies | where name has '/_api/cms/' | where success == false | summarize count() by resultCode, name` |
| Pages by P95 (30 d) | barchart | `pageViews | where isnotempty(customDimensions.PortalId) | summarize p95=percentile(duration, 95) by name | top 25 by p95 desc` |
| Exception trend on portal pages | timechart | `exceptions | where operation_Name has '/_api/cms/' or cloud_RoleName has 'portal' | summarize count() by bin(timestamp, 1h), outerMessage` |

## Flagship tile — paste & run

### Tile timelines/01 · Top 10 slowest portal pages — hourly P95 (7 d)

**Viz:** timechart
**Source:** [`./timelines/01-portal-top-slow-pages-hourly-7d.kql`](./timelines/01-portal-top-slow-pages-hourly-7d.kql)

The single most useful tile for "the site has been slow". Hourly P95 reveals daily peak windows (lunchtime, post-marketing-email surges) the daily averages flatten out.

## How to (re)generate in Azure Data Explorer dashboards

1. Create dashboard `Power Pages portal performance`.
2. Add your App Insights resource as a data source.
3. Single page to start; add tiles as you author them.
4. Add `_startTime`, `_endTime`, optional `_portalId` as dashboard parameters.

## Regenerate with GitHub Copilot

> *"@workspace Use [`DASHBOARD-portal-perf.md`](./DASHBOARD-portal-perf.md). Regenerate the existing tile and use the **Recommended additions** table to scaffold the missing `.kql` files in `kql/powerpages/` — name them following the repo's numeric-prefix convention. Cluster URI `<...>`, database `<...>`."*

Symptom-driven:

> *"@workspace Customers are reporting the homepage is slow today. Use this dashboard plus [`../_shared/exceptions/03-top10-real-problems-7d.kql`](../_shared/exceptions/03-top10-real-problems-7d.kql) — start with timelines/01 to confirm, then look at the noise-filtered exceptions."*

## Related dashboards

- [`../_shared/DASHBOARD-overview.md`](../_shared/DASHBOARD-overview.md) — confirm `pageViews` channel split first
- [`../modeldrivenapp/DASHBOARD-uci-form-perf.md`](../modeldrivenapp/DASHBOARD-uci-form-perf.md) — same `pageViews` table, different channel
- [`../dataverse/DASHBOARD-plugin-and-webapi-health.md`](../dataverse/DASHBOARD-plugin-and-webapi-health.md) — portal CMS routes lean on Dataverse Web API server-side
