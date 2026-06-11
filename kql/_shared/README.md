# _shared/

Cross-component queries and reusable building blocks. **Start here** when you don't know which component owns the data, or when a query intentionally spans multiple components (e.g. compare MDA `pageViews` to Power Pages `pageViews`).

## Subfolders

| Folder | Purpose |
|---|---|
| [`exceptions/`](exceptions/README.md) | Server-side exception noise catalog + reusable `_IsNoise` lambda + signal-vs-noise breakdowns. Applies to any Dataverse-backed component. |
| [`overview/`](overview/README.md) | Cross-table starting points — top pageViews, walk a single `operation_Id`, Log Analytics output template. |
| [`timelines/`](timelines/README.md) | Cross-component time series — `pageViews` split by channel (MDA vs Portal vs Other), all-tables 24 h pulse, weekly 90 d roll-up, exceptions trend. |
| [`cost/`](cost/README.md) | Ingestion-cost control — daily billable GB by table, noisiest custom-event / trace signals (sampling candidates). |
