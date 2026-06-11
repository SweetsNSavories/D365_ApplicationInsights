#!/usr/bin/env python
"""Validate generated live dashboard manifests and notebooks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KQL_ROOT = ROOT / "kql"


def validate_json_assets(min_tiles: int, max_tiles: int) -> list[str]:
    errors: list[str] = []
    manifest_paths = sorted(KQL_ROOT.rglob("LIVE-DASHBOARD.json"))
    notebook_paths = sorted(KQL_ROOT.rglob("LIVE-DASHBOARD.ipynb"))
    if not manifest_paths:
        errors.append("No LIVE-DASHBOARD.json files found.")
    if len(manifest_paths) != len(notebook_paths):
        errors.append(f"Manifest/notebook count mismatch: {len(manifest_paths)} vs {len(notebook_paths)}.")

    for path in manifest_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        tiles = data.get("tiles", [])
        if not (min_tiles <= len(tiles) <= max_tiles):
            errors.append(f"{path}: expected {min_tiles}-{max_tiles} tiles, found {len(tiles)}.")
        for tile in tiles:
            query_file = tile.get("queryFile")
            if not query_file:
                errors.append(f"{path}: tile missing queryFile: {tile}")
                continue
            query_path = (path.parent / query_file).resolve()
            if not query_path.exists():
                errors.append(f"{path}: missing query file {query_file}.")

    for path in notebook_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid notebook JSON: {exc}")
            continue
        for index, cell in enumerate(data.get("cells", []), start=1):
            metadata = cell.get("metadata", {})
            if "language" not in metadata:
                errors.append(f"{path}: cell {index} missing metadata.language.")
            if cell.get("cell_type") not in {"markdown", "code"}:
                errors.append(f"{path}: cell {index} has unsupported cell_type {cell.get('cell_type')!r}.")

    return errors


def dry_run_manifests() -> list[str]:
    errors: list[str] = []
    runner = ROOT / "tools" / "live_dashboard_runner.py"
    for manifest in sorted(KQL_ROOT.rglob("LIVE-DASHBOARD.json")):
        output = manifest.parent / "live-output"
        command = [sys.executable, str(runner), "--manifest", str(manifest), "--output", str(output), "--dry-run"]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        if completed.returncode != 0:
            errors.append(f"{manifest}: dry-run failed: {completed.stderr or completed.stdout}")
            continue
        for expected in ["index.html", "observations.md", "results.json"]:
            if not (output / expected).exists():
                errors.append(f"{manifest}: dry-run did not write {expected}.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate live dashboard generated assets.")
    parser.add_argument("--min-tiles", type=int, default=10)
    parser.add_argument("--max-tiles", type=int, default=15)
    parser.add_argument("--dry-run", action="store_true", help="Dry-run every manifest through the runner.")
    args = parser.parse_args()

    errors = validate_json_assets(args.min_tiles, args.max_tiles)
    if args.dry_run:
        errors.extend(dry_run_manifests())

    manifest_count = len(list(KQL_ROOT.rglob("LIVE-DASHBOARD.json")))
    notebook_count = len(list(KQL_ROOT.rglob("LIVE-DASHBOARD.ipynb")))
    print(f"Manifests: {manifest_count}")
    print(f"Notebooks: {notebook_count}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Live dashboard assets validated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())