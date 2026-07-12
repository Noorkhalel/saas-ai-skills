"""Privacy-preserving reference-load telemetry and aggregation."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "shared" / "reference-catalog.json"
OUTPUT = ROOT / "eval-results"
EVENTS = OUTPUT / "reference-telemetry.jsonl"


def _catalog() -> dict[str, Any]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def load_references(skill: str, request: str) -> list[str]:
    """Load only request-relevant skill references and record metadata, never text.

    Loaded bytes stay in process and are not returned to telemetry or reports.
    """
    entries = [item for item in _catalog()["references"] if item["skill"] == skill]
    tokens = {token for token in request.lower().replace("-", " ").split() if len(token) > 2}
    selected = []
    for item in entries:
        filename_tokens = {token for token in Path(item["path"]).stem.replace("-", " ").split() if len(token) > 2}
        if tokens & filename_tokens:
            selected.append(item)
    # A report template is foundational whenever available; otherwise no document
    # is loaded merely to create telemetry noise.
    selected.extend(item for item in entries if item["path"].endswith("report-schema.md") and item not in selected)
    names: list[str] = []
    OUTPUT.mkdir(exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as stream:
        for item in selected:
            started = time.perf_counter()
            try:
                (ROOT / item["path"]).read_bytes()
            except OSError:
                continue
            duration = round((time.perf_counter() - started) * 1000, 3)
            event = {"timestamp": datetime.now(timezone.utc).isoformat(), "skill": skill, "reference_filename": item["path"], "load_duration_ms": duration}
            stream.write(json.dumps(event, sort_keys=True) + "\n")
            names.append(item["path"])
    return names


def generate_report() -> dict[str, Any]:
    catalog = _catalog()["references"]
    counts: dict[tuple[str, str], dict[str, Any]] = {}
    if EVENTS.is_file():
        for line in EVENTS.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
                key = (event["skill"], event["reference_filename"])
                current = counts.setdefault(key, {"skill": key[0], "reference_filename": key[1], "load_count": 0, "load_duration_ms_total": 0.0})
                current["load_count"] += 1; current["load_duration_ms_total"] += float(event.get("load_duration_ms", 0))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
    all_rows = [{"skill": item["skill"], "reference_filename": item["path"], "load_count": counts.get((item["skill"], item["path"]), {}).get("load_count", 0), "load_duration_ms_total": counts.get((item["skill"], item["path"]), {}).get("load_duration_ms_total", 0.0)} for item in catalog]
    by_hash: dict[str, list[str]] = {}
    for item in catalog: by_hash.setdefault(item["sha256"], []).append(item["path"])
    duplicates = [paths for paths in by_hash.values() if len(paths) > 1]
    return {"schema_version": "1.0", "privacy": "reference usage metadata only; no user request, repository content, or reference text", "frequently_loaded": sorted((row for row in all_rows if row["load_count"]), key=lambda row: (-row["load_count"], row["reference_filename"]))[:20], "never_used": [row for row in all_rows if not row["load_count"]], "duplicate_references": duplicates, "consolidation_candidates": [paths for paths in duplicates if all(next(row["load_count"] for row in all_rows if row["reference_filename"] == path) < 2 for path in paths)]}


def write_report() -> None:
    OUTPUT.mkdir(exist_ok=True); report = generate_report()
    (OUTPUT / "reference-telemetry-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Reference telemetry report", "", report["privacy"], "", "## Frequently loaded", ""]
    lines += [f"- `{row['reference_filename']}` ({row['skill']}): {row['load_count']}" for row in report["frequently_loaded"]] or ["- None recorded."]
    lines += ["", "## Never used", "", *[f"- `{row['reference_filename']}` ({row['skill']})" for row in report["never_used"]], "", "## Duplicate references", ""]
    lines += [f"- {', '.join(paths)}" for paths in report["duplicate_references"]] or ["- None detected."]
    (OUTPUT / "reference-telemetry-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
