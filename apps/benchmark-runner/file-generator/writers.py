# ==============================================================================
# File: apps/benchmark-runner/file-generator/writers.py
# Purpose: Append-only CSV + JSONL. Never overwrite or truncate existing files.
# SOLID: SRP — persist rows. Callers (main.py / PowerShell twins) build models.
# Dependencies: models.py, stdlib csv + json, reports/history/.
# ==============================================================================
"""Append helpers for reports/history. Missing files get a header; existing stay."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Mapping, Sequence

from models import RESULT_CSV_COLUMNS, SERVICE_CSV_COLUMNS

# This package lives in apps/benchmark-runner/file-generator.
HISTORY_DIR = Path(__file__).resolve().parent.parent / "reports" / "history"

KIND_STEMS: dict[str, str] = {
    "manual": "manual_results",
    "automated": "automated_results",
    "performance": "performance_results",
    "security": "performance_results",
    "service": "service_runs",
}


def history_paths(kind: str) -> tuple[Path, Path]:
    """Return (csv_path, jsonl_path) for a --kind bucket. Raises on unknown kind."""
    key = kind.lower()
    if key not in KIND_STEMS:
        known = ", ".join(sorted(KIND_STEMS))
        raise ValueError(f"Unknown kind '{kind}'. Known: {known}")
    stem = KIND_STEMS[key]
    return HISTORY_DIR / f"{stem}.csv", HISTORY_DIR / f"{stem}.jsonl"


def _columns_for_kind(kind: str) -> Sequence[str]:
    """CSV header for test-result kinds vs service_runs."""
    if kind.lower() == "service":
        return SERVICE_CSV_COLUMNS
    return RESULT_CSV_COLUMNS


def _csv_needs_header(path: Path) -> bool:
    """True when the file is missing or empty. Never rewrite a non-empty file."""
    return not path.exists() or path.stat().st_size == 0


def append_csv(path: Path, row: Mapping[str, object], columns: Sequence[str]) -> None:
    """Append one CSV row. Write the header first if the file is new/empty.

    Never truncates an existing file with data. If a header-only file is present
    it is left intact and a data row is appended.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = _csv_needs_header(path)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(columns),
            extrasaction="ignore",
            lineterminator="\n",
        )
        if write_header:
            writer.writeheader()
        payload = {col: row.get(col, "") for col in columns}
        writer.writerow(payload)


def append_jsonl(path: Path, row: Mapping[str, object]) -> None:
    """Append one compact JSON object as a line. Never overwrites the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(row), ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def append_history(kind: str, row: Mapping[str, object]) -> tuple[Path, Path]:
    """Append the same row to the kind's CSV and JSONL. Returns both paths."""
    csv_path, jsonl_path = history_paths(kind)
    columns = _columns_for_kind(kind)
    append_csv(csv_path, row, columns)
    append_jsonl(jsonl_path, {col: row.get(col, "") for col in columns})
    return csv_path, jsonl_path
