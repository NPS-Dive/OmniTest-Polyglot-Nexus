# ==============================================================================
# File: apps/benchmark-runner/file-generator/models.py
# Purpose: Typed rows for append-only history (test results + service probes).
# SOLID: SRP — data shapes only. No filesystem I/O (writers.py owns that).
# Dependencies: Python 3.10+ stdlib dataclasses.
# ==============================================================================
"""Row types for benchmark-runner reports/history."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp (same spirit as PowerShell 'o' format)."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ResultRow:
    """One append-only history row (manual / automated / performance / security).

    Field names match CSV headers except ``passed``, which serializes as ``pass``.
    """

    test_name: str
    test_type: str
    language: str
    timestamp_utc: str = field(default_factory=utc_now_iso)
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p98_ms: float = 0.0
    p99_ms: float = 0.0
    ttl_ms: float = 0.0
    p50_ms: float = 0.0
    avg_ms: float = 0.0
    max_ms: float = 0.0
    iterations: int = 1
    vus: int = 1
    fail_rate: float = 0.0
    passed: bool = False
    error_message: str = ""

    def to_history_dict(self) -> dict:
        """Map to the locked CSV/JSONL column names (``pass``, not ``passed``)."""
        raw = asdict(self)
        raw["language"] = self.language.lower()
        raw["pass"] = self.passed
        del raw["passed"]
        return raw


# Locked column order — must match ReportWriter.ps1 Get-OpnHistoryHeader.
RESULT_CSV_COLUMNS: tuple[str, ...] = (
    "timestamp_utc",
    "test_name",
    "test_type",
    "language",
    "p90_ms",
    "p95_ms",
    "p98_ms",
    "p99_ms",
    "ttl_ms",
    "p50_ms",
    "avg_ms",
    "max_ms",
    "iterations",
    "vus",
    "fail_rate",
    "pass",
    "error_message",
)


@dataclass
class ServiceRunRow:
    """One liveness/probe row for service_runs.csv / .jsonl."""

    language: str
    port: int
    timestamp_utc: str = field(default_factory=utc_now_iso)
    up: bool = False
    latency_ms: float = 0.0
    error_message: str = ""

    def to_history_dict(self) -> dict:
        """Map to service_runs column names."""
        raw = asdict(self)
        raw["language"] = self.language.lower()
        return raw


# Locked column order — must match ReportWriter.ps1 Get-OpnServiceRunHeader.
SERVICE_CSV_COLUMNS: tuple[str, ...] = (
    "timestamp_utc",
    "language",
    "port",
    "up",
    "latency_ms",
    "error_message",
)
