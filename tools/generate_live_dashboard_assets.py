#!/usr/bin/env python
"""Generate LIVE-DASHBOARD.json manifests and notebooks for KQL folders."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KQL_ROOT = ROOT / "kql"
MIN_TILES = 10
MAX_TILES = 15

APPINSIGHTS_BASELINE = [
    "kql/_shared/timelines/06-all-tables-pulse-24h.kql",
    "kql/_shared/timelines/01-pageviews-daily-30d-by-channel.kql",
    "kql/_shared/timelines/02-pageviews-hourly-7d-by-channel.kql",
    "kql/_shared/timelines/03-pageviews-duration-percentiles-30d.kql",
    "kql/_shared/timelines/05-exceptions-daily-30d-top-problems.kql",
    "kql/_shared/exceptions/01-noise-catalog-breakdown-7d.kql",
    "kql/_shared/exceptions/03-top10-real-problems-7d.kql",
    "kql/_shared/exceptions/04-exceptions-signal-vs-noise-30d.kql",
    "kql/_shared/exceptions/06-noise-discovery-candidates-7d.kql",
    "kql/_shared/cost/01-ingestion-volume-by-table-30d.kql",
    "kql/_shared/cost/02-noisy-signals-candidates-for-sampling.kql",
    "kql/_shared/overview/02-pageviews-by-operation-id.kql",
]


def title_from_filename(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"^\d+-", "", stem)
    stem = stem.replace("-", " ")
    return stem[:1].upper() + stem[1:]


def discover_dashboard(folder: Path) -> Path | None:
    dashboards = sorted(folder.glob("DASHBOARD-*.md"))
    return dashboards[0] if dashboards else None


def parse_dashboard_tiles(dashboard: Path) -> list[dict[str, str]]:
    tiles: list[dict[str, str]] = []
    pattern = re.compile(r"\[`?([^`\]]+?\.kql)`?\]\(([^)]+\.kql)\)")
    for line in dashboard.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or ".kql" not in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 4 or parts[0] in {"---", "#"}:
            continue
        match = pattern.search(line)
        if not match:
            continue
        title = parts[1] if len(parts) > 1 else title_from_filename(Path(match.group(2)))
        viz = parts[2] if len(parts) > 2 else "table"
        what = parts[4] if len(parts) > 4 else "Run this tile and inspect returned rows."
        tiles.append({"title": title, "viz": viz, "queryFile": match.group(2), "observationFocus": what})
    return tiles


def direct_kql_tiles(folder: Path) -> list[dict[str, str]]:
    tiles = []
    for path in sorted(folder.glob("*.kql")):
        tiles.append(
            {
                "title": title_from_filename(path),
                "viz": "table",
                "queryFile": path.name,
                "observationFocus": "Run this query and inspect returned rows for spikes, top offenders, and zero-row surprises.",
            }
        )
    return tiles


def descendant_kql_tiles(folder: Path) -> list[dict[str, str]]:
    tiles = []
    for path in sorted(folder.rglob("*.kql")):
        relative = path.relative_to(folder).as_posix()
        tiles.append(
            {
                "title": title_from_filename(path),
                "viz": "table",
                "queryFile": relative,
                "observationFocus": "Cross-folder live tile. Inspect returned rows and choose the next component drill-down.",
            }
        )
    return tiles


def normalize_query_file(folder: Path, query_file: str) -> str:
    while query_file.startswith("./"):
        query_file = query_file[2:]
    candidate = (folder / query_file).resolve()
    if candidate.exists():
        return query_file.replace("\\", "/")
    repo_candidate = (ROOT / query_file).resolve()
    if repo_candidate.exists():
        return repo_candidate.relative_to(folder).as_posix()
    return query_file.replace("\\", "/")


def unique_tiles(folder: Path, tiles: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    output = []
    for tile in tiles:
        query_file = normalize_query_file(folder, tile["queryFile"])
        key = str((folder / query_file).resolve())
        if key in seen or not (folder / query_file).exists():
            continue
        seen.add(key)
        updated = dict(tile)
        updated["queryFile"] = query_file
        output.append(updated)
    return output


def supplement_tiles(folder: Path, existing: list[dict[str, str]], runtime: str) -> list[dict[str, str]]:
    if runtime == "resourcegraph":
        return existing[:MAX_TILES]
    tiles = list(existing)
    for repo_path in APPINSIGHTS_BASELINE:
        path = ROOT / repo_path
        tiles.append(
            {
                "title": f"Context: {title_from_filename(path)}",
                "viz": "table",
                "queryFile": Path(os.path.relpath(path, folder)).as_posix(),
                "observationFocus": "Shared context tile used to baseline telemetry, noise, or ingestion before component drill-down.",
            }
        )
    return unique_tiles(folder, tiles)[:MAX_TILES]


def folder_display_name(folder: Path) -> str:
    if folder == KQL_ROOT:
        return "All KQL"
    return folder.relative_to(KQL_ROOT).as_posix().replace("/", " / ")


def build_manifest(folder: Path) -> dict:
    dashboard = discover_dashboard(folder)
    runtime = "resourcegraph" if "resourcegraph" in folder.parts else "appinsights"
    if dashboard:
        tiles = parse_dashboard_tiles(dashboard)
    else:
        tiles = direct_kql_tiles(folder)
    if not tiles and folder in {KQL_ROOT, KQL_ROOT / "_shared", KQL_ROOT / "fno"}:
        tiles = descendant_kql_tiles(folder)
    tiles = supplement_tiles(folder, unique_tiles(folder, tiles), runtime)
    return {
        "name": f"Live Dashboard - {folder_display_name(folder)}",
        "runtime": runtime,
        "description": "Run these KQL tiles against a customer environment, render results, and capture observations.",
        "sourceDashboard": dashboard.name if dashboard else "",
        "minimumTargetTiles": MIN_TILES,
        "maximumTargetTiles": MAX_TILES,
        "tiles": [dict({"id": f"tile-{index:02d}"}, **tile) for index, tile in enumerate(tiles, start=1)],
    }


def notebook_for(folder: Path) -> dict:
    title = folder_display_name(folder)
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {"language": "markdown"},
                "source": [
                    f"# Live Dashboard - {title}\n",
                    "Run this notebook in a customer workspace to execute the folder's KQL tiles, generate local dashboard output, and capture observations.\n",
                    "Customer data is written only to the local `live-output/` folder, which is ignored by Git.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"language": "python"},
                "outputs": [],
                "source": [
                    "from pathlib import Path\n",
                    "import subprocess\n",
                    "import sys\n",
                    "\n",
                    "def find_repo_root(start: Path) -> Path:\n",
                    "    for candidate in [start, *start.parents]:\n",
                    "        if (candidate / 'tools' / 'live_dashboard_runner.py').exists():\n",
                    "            return candidate\n",
                    "    raise RuntimeError('Could not find repository root containing tools/live_dashboard_runner.py')\n",
                    "\n",
                    "REPO_ROOT = find_repo_root(Path.cwd().resolve())\n",
                    "MANIFEST = Path.cwd() / 'LIVE-DASHBOARD.json'\n",
                    "OUTPUT_DIR = Path.cwd() / 'live-output'\n",
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {"language": "markdown"},
                "source": [
                    "## Configure\n",
                    "Set `DRY_RUN = False` and provide either `APPINSIGHTS_RESOURCE_ID`, `WORKSPACE_ID`, or `SUBSCRIPTIONS` depending on the manifest runtime.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"language": "python"},
                "outputs": [],
                "source": [
                    "DRY_RUN = True\n",
                    "APPINSIGHTS_RESOURCE_ID = ''  # /subscriptions/<sub>/resourceGroups/<rg>/providers/microsoft.insights/components/<name>\n",
                    "WORKSPACE_ID = ''             # Optional Log Analytics workspace ID\n",
                    "SUBSCRIPTIONS = ''           # Comma-separated subscription IDs for Azure Resource Graph manifests\n",
                    "TIMESPAN_DAYS = 30\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {"language": "python"},
                "outputs": [],
                "source": [
                    "cmd = [\n",
                    "    sys.executable, str(REPO_ROOT / 'tools' / 'live_dashboard_runner.py'),\n",
                    "    '--manifest', str(MANIFEST),\n",
                    "    '--output', str(OUTPUT_DIR),\n",
                    "    '--timespan-days', str(TIMESPAN_DAYS),\n",
                    "]\n",
                    "if DRY_RUN:\n",
                    "    cmd.append('--dry-run')\n",
                    "if APPINSIGHTS_RESOURCE_ID:\n",
                    "    cmd.extend(['--appinsights-resource-id', APPINSIGHTS_RESOURCE_ID])\n",
                    "if WORKSPACE_ID:\n",
                    "    cmd.extend(['--workspace-id', WORKSPACE_ID])\n",
                    "if SUBSCRIPTIONS:\n",
                    "    cmd.extend(['--subscriptions', SUBSCRIPTIONS])\n",
                    "print('Running:', ' '.join(cmd))\n",
                    "completed = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)\n",
                    "print(completed.stdout)\n",
                    "if completed.stderr:\n",
                    "    print(completed.stderr)\n",
                    "if completed.returncode != 0:\n",
                    "    raise SystemExit(completed.returncode)\n",
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {"language": "markdown"},
                "source": [
                    "## Review Output\n",
                    "Open `live-output/index.html` for the rendered dashboard and `live-output/observations.md` for the observation log.\n",
                    "Re-run with `DRY_RUN = False` after confirming credentials and RBAC.\n",
                ],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def target_folders() -> list[Path]:
    folders = {path.parent for path in KQL_ROOT.rglob("*.kql")}
    folders.update(path.parent for path in KQL_ROOT.rglob("DASHBOARD-*.md"))
    folders.update({KQL_ROOT, KQL_ROOT / "_shared", KQL_ROOT / "fno"})
    return sorted(folders)


def main() -> int:
    generated = 0
    for folder in target_folders():
        manifest = build_manifest(folder)
        if not manifest["tiles"]:
            continue
        (folder / "LIVE-DASHBOARD.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (folder / "LIVE-DASHBOARD.ipynb").write_text(json.dumps(notebook_for(folder), indent=2), encoding="utf-8")
        generated += 1
    print(f"Generated live dashboard assets for {generated} folder(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())