# powerpages/

Power Pages (formerly Power Apps Portals) telemetry — public/authenticated portal pages, page perf, anonymous vs authenticated.

## Discriminator

A `pageViews` row belongs to Power Pages if `customDimensions.PortalId` is populated. (If `appModule` is populated → see [`../modeldrivenapp/`](../modeldrivenapp/README.md).)

## Files (top level)

_No top-level files yet._ Drop new portal-specific queries here.

## Files ([`timelines/`](timelines/))

| # | File | What it does |
|---|---|---|
| 01 | [`timelines/01-portal-top-slow-pages-hourly-7d.kql`](timelines/01-portal-top-slow-pages-hourly-7d.kql) | Top 10 slowest portal pages, hourly P95, last 7 days |

## Suggested queries to add

- `pageViews` daily by `customDimensions.PortalId` (split tenants/sites)
- Authenticated vs anonymous (`user_AuthenticatedId` populated)
- Top server-side `customDimensions.RequestProperty.cmscontent_uri` paths
- Form submission failures (look at `dependencies` to `_api/cms/...` with `success==false`)

## Provenance

- `timelines/01` → locally authored.
