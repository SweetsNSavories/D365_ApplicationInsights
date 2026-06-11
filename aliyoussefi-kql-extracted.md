# KQL extracted from aliyoussefi repos

Sources:

- [aliyoussefi/D365-Monitoring](https://github.com/aliyoussefi/D365-Monitoring) — 4 KQL files at repo root (`KustoQueries.*.txt`)
- [aliyoussefi/MonitoringPowerPlatform](https://github.com/aliyoussefi/MonitoringPowerPlatform) — KQL embedded in `docs/*.md`

All queries below target **Azure Application Insights** (classic schema: `requests`, `dependencies`, `pageViews`, `customEvents`, `customMetrics`, `exceptions`, `traces`, `browserTimings`, `availabilityResults`) unless noted otherwise.

---

## D365-Monitoring — `KustoQueries.CustomEvents.txt`

### General example: parse `customDimensions` and `customMeasurements`

```kql
customEvents
| where name == "sample"
| extend cd = parse_json(customDimensions)
| extend cm = parse_json(customMeasurements)
| order by timestamp desc
```

### Parsing and converting — Canvas/Web Resource client perf

```kql
customEvents
| extend cd = parse_json(customDimensions)
| extend cm = parse_json(customMeasurements)
| project
    timestamp,
    cd.client,
    name,
    cd.userName,
    toint(cm.DomContentLoadTime),
    toint(cm.RequestResponseTime),
    toint(cm.PageRenderTime),
    toint(cm.NetworkLatency),
    toint(cm.RedirectCount)
```

### Focus on Web Resource / Client events with client info

```kql
customEvents
| extend cd = parse_json(customDimensions)
| extend cm = parse_json(customMeasurements)
| project
    timestamp,
    name,
    cd,
    cm,
    client_Type,
    client_OS,
    client_StateOrProvince,
    client_Browser
```

### Parsing serialized `RemoteExecutionContext` (D365 plug-in)

```kql
customEvents
| extend context = parse_json(customDimensions)
| extend rmc = parse_json(context)
| order by timestamp desc
| project context.RemoteExecutionContext, rmc.BusinessUnitId
```

---

## D365-Monitoring — `KustoQueries.PageViews.txt`

### Records coming from a Generic Smartphone

```kql
pageViews
| where client_Model == "Generic Smartphone"
```

### Check for specific browser and OS (Windows, non-Chrome, slow)

```kql
pageViews
| extend cm = parse_json(customMeasurements)
| extend cd = parse_json(customDimensions)
| where duration > 20
| where client_Browser !contains "Chrome"
| where client_OS contains "Windows"
```

---

## D365-Monitoring — `KustoQueries.Exceptions.txt`

### Exceptions from iOS

```kql
exceptions
| where client_Browser == "Mobile Safari UI/WKWebView 12.0"
```

### Exceptions from non-Web clients

```kql
exceptions
| extend d  = parse_json(details)
| extend cm = parse_json(customMeasurements)
| extend cd = parse_json(customDimensions)
| where cd.client != "Web"
| project
    timestamp, problemId, type, assembly, method,
    d[0].type, d[0].parsedStack[0].line,
    cd.userName, cd.uniqueName, client_OS, client_Browser, cd
```

### Exceptions from browsers

```kql
exceptions
| extend d  = parse_json(details)
| extend cm = parse_json(customMeasurements)
| extend cd = parse_json(customDimensions)
| where client_Type == "Browser"
| project
    timestamp, problemId, type, assembly, method,
    d[0].type, d[0].parsedStack[0].line,
    cd.userName, cd.uniqueName, client_OS, client_Browser, cd
```

---

## D365-Monitoring — `KustoQueries.CustomMetrics.txt`

### Web Resource request durations / record counts

```kql
customMetrics
| extend cd = parse_json(customDimensions)
| where cd.Source == "WebResource"
| order by timestamp desc
| project
    timestamp,
    cd.Verb,
    cd.URL,
    requestDurationMS = value,
    countOfRecords   = valueCount,
    cd.RequestLimits,
    name,
    cd
```

---

## MonitoringPowerPlatform — Canvas Apps (`docs/02.04 …Getting Started with Application Insights.md`)

### Pull `ms-app*` identifiers from `customDimensions`

```kql
// This query shows how to parse customDimensions for the app identifiers
traces
| union pageViews, customEvents, browserTimings
| extend cd = parse_json(customDimensions)
| project
    timestamp,
    itemId,                                       // changes per call
    itemType,
    operation_Id, operation_ParentId,             // does NOT change per call
    operation_Name, session_Id, user_Id,
    message,
    cd.['ms-appSessionId'], cd.['ms-appName'], cd.['ms-appId']
```

### Page views within the same session

```kql
// Follow a user's path in the canvas app via session_Id
pageViews
// | where session_Id == "f8Pae"   // Windows 10
// | where session_Id == "YhUhd"   // iOS
| where timestamp between (datetime(2020-05-13T10:02:52.137Z) .. datetime(2020-05-14T12:04:52.137Z))
```

### Slowest pages / screens (top 3, piechart)

```kql
// What are the 3 slowest pages, and how slow are they?
pageViews
| where notempty(duration) and client_Type == 'Browser'
| extend total_duration = duration * itemCount
| summarize avg_duration = (sum(total_duration) / sum(itemCount)) by operation_Name
| top 3 by avg_duration desc
| render piechart
```

### Connecting the dots — full session timeline (union across all tables)

```kql
union (traces), (requests), (pageViews), (dependencies),
      (customEvents), (availabilityResults), (exceptions)
| extend itemType = iif(itemType == 'availabilityResult', itemType,
                    iif(itemType == 'customEvent',        itemType,
                    iif(itemType == 'dependency',         itemType,
                    iif(itemType == 'pageView',           itemType,
                    iif(itemType == 'request',            itemType,
                    iif(itemType == 'trace',              itemType,
                    iif(itemType == 'exception',          itemType, "")))))))
| where
    (
        (itemType == 'request' or itemType == 'trace' or itemType == 'exception'
         or itemType == 'dependency' or itemType == 'availabilityResult'
         or itemType == 'pageView' or itemType == 'customEvent')
        and
        (timestamp between (datetime(2020-04-26T05:17:59.459Z) .. datetime(2020-04-27T05:17:59.459Z)))
        and
        session_Id == 'tmcZK'
    )
| top 101 by timestamp desc
```

---

## MonitoringPowerPlatform — Monitor Tool extractor (`docs/02.03 … Monitor Tool Part 2 …`)

These run over App Insights data populated by the `BlobTriggeredMonitorToolToApplicationInsights` Azure Function ([sample](https://github.com/aliyoussefi/MonitoringPowerPlatform/tree/main/Samples/ModelApps/MonitorToolExtractor)) that funnels Monitor Tool JSON into `customEvents`, `requests`, `dependencies`, `pageViews`.

### Review performance messages

```kql
customEvents
| extend cd = parse_json(customDimensions)
| where cd.messageCategory == "Performance"
| project session_Id, name, cd.dataSource
```

### Browser requests — method, code, duration, sync

```kql
// Request Method, ResultCode, Duration and Sync
requests
| extend cd   = parse_json(customDimensions)
| extend data = parse_json(tostring(cd.data))
| project
    session_Id, name,
    data.method, resultCode, data.name,
    data.duration, data.sync,
    cd.fileName
```

### Browser requests — with full resource timings

```kql
// Request Method, ResultCode, Duration and Resource Timings
requests
| extend cd   = parse_json(customDimensions)
| extend data = parse_json(tostring(cd.data))
| project
    session_Id, name, data.method, resultCode, data.name, data.duration,
    data.startTime,
    data.fetchStart,
    data.domainLookupStart,
    data.connectStart,
    data.requestStart,
    data.responseStart,
    data.responseEnd
```

### Key Performance Indicators — FullLoad attribution

```kql
pageViews
| extend cd          = parse_json(customDimensions)
| extend cm          = parse_json(customMeasurements)
| extend data        = parse_json(tostring(cd.data))
| extend attribution = parse_json(tostring(data.Attribution))
| where name == "FullLoad"
| order by tostring(data.FirstInteractionTime), toint(cm.duration)
| project session_Id, name, data.FirstInteractionTime, cm.duration, attribution
```

---

## MonitoringPowerPlatform — Power Automate / Canvas Apps audit via Log Analytics

These are **Azure Log Analytics** (`AzureDiagnostics`) queries, not App Insights. Used to surface Logic-Apps-style output captured from Office 365 Unified Audit Log routed through Azure Automation / Event Hub.

`docs/04.02.02 … Power Automate Auditing Part 2.md` and `docs/02.02.02 … Canvas Apps Auditing Part 2.md`:

```kql
AzureDiagnostics
| where StreamType_s == "Output"
| project TimeGenerated, ResultDescription
```

---

## What ISN'T KQL in these repos

For completeness, neither repo ships additional `.kql`/`.csl` files or workbook templates. The remainder of both repos is:

- **D365-Monitoring** — plug-ins (`Dynamics365.Monitoring.Plugins/*.cs`), web resources (`ApplicationInsightsDemo*.js`, `tracktelemetry.js`), Azure Functions, the `Dataverse.Monitoring.Sdk` console app, and PowerShell examples that *write* telemetry. No additional KQL.
- **MonitoringPowerPlatform** — PCF control (`Samples/PCF/AppInsights/index.ts`), Power Pages JS-SDK snippet (`Samples/PowerAppsPortals/AppInsights/JS-SDK-Snippet.js`), the Monitor Tool extractor Azure Function, and a long set of blog-backup HTML/MD docs. The only KQL in this repo is what's reproduced above.

---

## Quick mapping for Power Pages / Dataverse telemetry

For any Power Platform App Insights workspace, the most directly reusable queries are:

| Use case | Query above |
| --- | --- |
| Slow Power Pages page-load top offenders | `pageViews → Slowest pages` |
| Per-session end-to-end timeline for a reported user issue | `Connecting the dots — full session timeline` |
| Mobile vs desktop performance split | `KustoQueries.PageViews.txt` queries |
| Plug-in / WebResource exception drill-down | `KustoQueries.Exceptions.txt` (non-Web + Browser) |
| Web-API request duration & rate-limit headers from D365 portal | `KustoQueries.CustomMetrics.txt` (`cd.RequestLimits`) |
| Parse `RemoteExecutionContext` from plug-in telemetry | `KustoQueries.CustomEvents.txt` (RemoteExecutionContext) |

Swap `client_Browser`, `session_Id`, and `operation_Name` literals for your environment's values before running.
