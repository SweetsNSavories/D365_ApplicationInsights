#!/usr/bin/env python
"""Run a live KQL dashboard manifest and write result artifacts.

The public repository contains generic KQL. Customer-specific results are written
to local output folders and should not be committed.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import sys
import traceback
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable


@dataclass
class TileResult:
    tile: dict[str, Any]
    query_path: str
    status: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    observations: list[str]
    error: str | None = None


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_query(manifest_path: Path, query_file: str) -> tuple[Path, str]:
    query_path = (manifest_path.parent / query_file).resolve()
    return query_path, query_path.read_text(encoding="utf-8-sig")


def query_appinsights(args: argparse.Namespace, query: str) -> tuple[list[str], list[dict[str, Any]]]:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.monitor.query import LogsQueryClient, LogsQueryStatus
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependencies. Install with: pip install -r requirements-live-dashboard.txt"
        ) from exc

    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    client = LogsQueryClient(credential)
    timespan = timedelta(days=args.timespan_days)
    if args.workspace_id:
        response = client.query_workspace(args.workspace_id, query, timespan=timespan)
    elif args.appinsights_resource_id:
        response = client.query_resource(args.appinsights_resource_id, query, timespan=timespan)
    else:
        raise RuntimeError("Provide --appinsights-resource-id or --workspace-id, or use --dry-run.")

    if response.status == LogsQueryStatus.PARTIAL:
        table = response.partial_data[0] if response.partial_data else None
    else:
        table = response.tables[0] if response.tables else None
    if table is None:
        return [], []
    columns = [column.name for column in table.columns]
    rows = [dict(zip(columns, row)) for row in table.rows]
    return columns, rows


def query_resource_graph(args: argparse.Namespace, query: str) -> tuple[list[str], list[dict[str, Any]]]:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resourcegraph import ResourceGraphClient
        from azure.mgmt.resourcegraph.models import QueryRequest
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependencies. Install with: pip install -r requirements-live-dashboard.txt"
        ) from exc

    subscriptions = [item.strip() for item in args.subscriptions.split(",") if item.strip()]
    if not subscriptions:
        raise RuntimeError("Provide --subscriptions for Azure Resource Graph manifests, or use --dry-run.")
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    client = ResourceGraphClient(credential)
    request = QueryRequest(subscriptions=subscriptions, query=query)
    response = client.resources(request)
    data = list(response.data or [])
    columns = sorted({key for row in data for key in row.keys()})
    rows = [{column: row.get(column) for column in columns} for row in data]
    return columns, rows


def numeric_value(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


def summarize_rows(tile: dict[str, Any], columns: list[str], rows: list[dict[str, Any]], status: str, error: str | None) -> list[str]:
    title = tile.get("title", "Tile")
    query_file = tile.get("queryFile", "")
    observations: list[str] = []
    if status == "dry-run":
        observations.append("Dry run only: query was found and validated for execution, but no customer data was queried.")
        observations.append("Run with an App Insights resource ID, workspace ID, or Resource Graph subscriptions to populate live results.")
        return observations
    if error:
        observations.append(f"Execution failed for {title}: {error}")
        observations.append("Check connection, RBAC, table names, placeholders, and query-specific parameters before using this tile.")
        return observations
    if not rows:
        observations.append("Returned zero rows. Verify time window, instrumentation, table naming, and placeholder filters before treating this as absence of the issue.")
        observations.append("If this tile should normally return data, run the all-table pulse and a raw sample query next.")
        return observations

    observations.append(f"Returned {len(rows)} row(s) with columns: {', '.join(columns[:8])}{'...' if len(columns) > 8 else ''}.")
    if rows:
        first = rows[0]
        preview = ", ".join(f"{key}={first.get(key)!r}" for key in columns[:4])
        observations.append(f"First row preview: {preview}.")

    numeric_columns = []
    for column in columns:
        values = [numeric_value(row.get(column)) for row in rows]
        values = [value for value in values if value is not None]
        if values:
            numeric_columns.append((column, max(values), min(values)))
    priority_terms = ("fail", "error", "exception", "p95", "p99", "duration", "count", "calls", "latency", "success")
    prioritized = [item for item in numeric_columns if any(term in item[0].lower() for term in priority_terms)]
    for column, maximum, minimum in (prioritized or numeric_columns)[:3]:
        observations.append(f"Numeric signal `{column}` ranges from {minimum:g} to {maximum:g} in the returned sample.")

    lower_text = f"{title} {query_file} {tile.get('observationFocus', '')}".lower()
    if any(term in lower_text for term in ("exception", "trace", "noise", "error")):
        observations.append("Noise caution: compare this result with the known-noise baseline and inspect raw rows before calling it actionable.")
    return observations


def normalize_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns or ["message"])
        writer.writeheader()
        for row in rows:
            writer.writerow({column: normalize_value(row.get(column)) for column in columns})


def render_table(columns: list[str], rows: list[dict[str, Any]], limit: int) -> str:
    if not rows:
        return "<p class='empty'>No rows returned.</p>"
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body_rows = []
    for row in rows[:limit]:
        cells = "".join(f"<td>{html.escape(str(normalize_value(row.get(column, ''))))}</td>" for column in columns)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def write_outputs(manifest: dict[str, Any], results: list[TileResult], output_dir: Path, preview_rows: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_dir = output_dir / "csv"
    csv_dir.mkdir(exist_ok=True)

    serializable = []
    for index, result in enumerate(results, start=1):
        csv_name = f"tile-{index:02d}.csv"
        write_csv(csv_dir / csv_name, result.columns, result.rows)
        serializable.append(
            {
                "tile": result.tile,
                "queryPath": result.query_path,
                "status": result.status,
                "columns": result.columns,
                "rowCount": result.row_count,
                "observations": result.observations,
                "error": result.error,
                "csv": str(Path("csv") / csv_name),
                "rowsPreview": [
                    {key: normalize_value(value) for key, value in row.items()} for row in result.rows[:preview_rows]
                ],
            }
        )
    (output_dir / "results.json").write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    md_lines = [f"# {manifest.get('name', 'Live dashboard')} Observations", ""]
    md_lines.append(f"Runtime: `{manifest.get('runtime', 'appinsights')}`")
    md_lines.append("")
    for index, result in enumerate(results, start=1):
        md_lines.extend(
            [
                f"## Tile {index:02d}: {result.tile.get('title', 'Untitled')}",
                "",
                f"- Query: `{result.query_path}`",
                f"- Status: `{result.status}`",
                f"- Rows: {result.row_count}",
                "- Observations:",
            ]
        )
        md_lines.extend(f"  - {observation}" for observation in result.observations)
        md_lines.append("")
    (output_dir / "observations.md").write_text("\n".join(md_lines), encoding="utf-8")

    cards = []
    for index, result in enumerate(results, start=1):
        observations = "".join(f"<li>{html.escape(item)}</li>" for item in result.observations)
        status_class = "ok" if result.status == "success" else "warn" if result.status == "dry-run" else "error"
        cards.append(
            f"""
            <section class="tile">
              <header><span>Tile {index:02d}</span><strong>{html.escape(result.tile.get('title', 'Untitled'))}</strong><em class="{status_class}">{html.escape(result.status)}</em></header>
              <p class="query">{html.escape(result.query_path)}</p>
              <div class="meta">Rows: {result.row_count} | Viz: {html.escape(str(result.tile.get('viz', 'table')))}</div>
              <h3>Observations</h3><ul>{observations}</ul>
              {render_table(result.columns, result.rows, preview_rows)}
            </section>
            """
        )
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(manifest.get('name', 'Live dashboard'))}</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f6f8fb; color: #1f2937; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
h1 {{ margin-bottom: 4px; }}
.subtitle {{ color: #5f6b7a; margin-top: 0; }}
.tile {{ background: white; border: 1px solid #d9e1ec; border-radius: 8px; margin: 18px 0; padding: 16px; box-shadow: 0 1px 2px rgba(15,23,42,.06); }}
.tile header {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
.tile header span {{ color: #2563eb; font-weight: 700; }}
.tile header strong {{ font-size: 16px; }}
.tile header em {{ margin-left: auto; font-style: normal; font-size: 12px; padding: 3px 8px; border-radius: 999px; }}
.ok {{ background: #dcfce7; color: #166534; }} .warn {{ background: #fef3c7; color: #92400e; }} .error {{ background: #fee2e2; color: #991b1b; }}
.query, .meta {{ color: #64748b; font-size: 13px; }}
table {{ width: 100%; border-collapse: collapse; display: block; overflow-x: auto; margin-top: 12px; }}
th, td {{ border: 1px solid #e5e7eb; padding: 6px 8px; text-align: left; vertical-align: top; font-size: 12px; }}
th {{ background: #f1f5f9; }}
.empty {{ color: #92400e; }}
</style>
</head>
<body><main>
<h1>{html.escape(manifest.get('name', 'Live dashboard'))}</h1>
<p class="subtitle">Generated live dashboard output. Customer-specific data stays local.</p>
{''.join(cards)}
</main></body></html>"""
    (output_dir / "index.html").write_text(html_doc, encoding="utf-8")


def execute_manifest(args: argparse.Namespace) -> list[TileResult]:
    manifest_path = Path(args.manifest).resolve()
    manifest = load_manifest(manifest_path)
    runtime = args.runtime or manifest.get("runtime", "appinsights")
    results: list[TileResult] = []
    for tile in manifest.get("tiles", []):
        query_path, query = read_query(manifest_path, tile["queryFile"])
        status = "success"
        columns: list[str] = []
        rows: list[dict[str, Any]] = []
        error = None
        try:
            if args.dry_run:
                status = "dry-run"
            elif runtime == "resourcegraph":
                columns, rows = query_resource_graph(args, query)
            else:
                columns, rows = query_appinsights(args, query)
        except Exception as exc:  # Keep the dashboard going so one bad tile does not hide the rest.
            status = "error"
            error = str(exc)
            if args.verbose:
                traceback.print_exc()
        observations = summarize_rows(tile, columns, rows, status, error)
        results.append(
            TileResult(
                tile=tile,
                query_path=str(query_path.relative_to(manifest_path.parent) if query_path.is_relative_to(manifest_path.parent) else query_path),
                status=status,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                observations=observations,
                error=error,
            )
        )
    write_outputs(manifest, results, Path(args.output), args.preview_rows)
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a live dashboard manifest and write observations.")
    parser.add_argument("--manifest", required=True, help="Path to LIVE-DASHBOARD.json")
    parser.add_argument("--output", required=True, help="Output folder for index.html, observations.md, results.json, and CSVs")
    parser.add_argument("--runtime", choices=["appinsights", "resourcegraph"], help="Override manifest runtime")
    parser.add_argument("--appinsights-resource-id", default="", help="Application Insights Azure resource ID")
    parser.add_argument("--workspace-id", default="", help="Log Analytics workspace ID")
    parser.add_argument("--subscriptions", default="", help="Comma-separated subscription IDs for Azure Resource Graph")
    parser.add_argument("--timespan-days", type=int, default=30, help="Timespan supplied to Azure Monitor Logs API")
    parser.add_argument("--preview-rows", type=int, default=25, help="Rows shown in HTML/results preview per tile")
    parser.add_argument("--dry-run", action="store_true", help="Validate manifest and write output shell without querying Azure")
    parser.add_argument("--verbose", action="store_true", help="Print stack traces for failed tiles")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = execute_manifest(args)
    failures = [result for result in results if result.status == "error"]
    print(f"Processed {len(results)} tile(s). Failures: {len(failures)}. Output: {args.output}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())