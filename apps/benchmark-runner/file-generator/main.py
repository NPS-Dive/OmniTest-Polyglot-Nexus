# ==============================================================================
# File: apps/benchmark-runner/file-generator/main.py
# Purpose: CLI composition root — append one history or service-run row.
# SOLID: SRP — argparse + assemble a dataclass. I/O stays in writers.py.
# Dependencies: models.py, writers.py, Python 3.10+ stdlib only.
# Usage:
#   python main.py --kind performance --language go --test-name K6-load-go --p99-ms 12 --pass
#   python main.py --kind service --language go --port 50054 --up --latency-ms 3
# ==============================================================================
"""Command-line entry for append-only OmniTest history files."""

from __future__ import annotations

import argparse
import sys

from models import ResultRow, ServiceRunRow
from writers import append_history


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI. ``--kind`` selects the target file pair."""
    parser = argparse.ArgumentParser(
        description="Append one row to reports/history (never overwrite).",
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=("service", "manual", "automated", "performance"),
        help="Which history pair to append (security shares performance files).",
    )
    parser.add_argument("--language", required=True, help="cpp|python|java|go|csharp|node")
    parser.add_argument("--test-name", default="", help="Required for non-service kinds.")
    parser.add_argument(
        "--test-type",
        default="",
        help="Defaults to --kind (manual|automated|performance).",
    )
    parser.add_argument("--p90-ms", type=float, default=0.0)
    parser.add_argument("--p95-ms", type=float, default=0.0)
    parser.add_argument("--p98-ms", type=float, default=0.0)
    parser.add_argument("--p99-ms", type=float, default=0.0)
    parser.add_argument("--ttl-ms", type=float, default=0.0)
    parser.add_argument("--p50-ms", type=float, default=0.0)
    parser.add_argument("--avg-ms", type=float, default=0.0)
    parser.add_argument("--max-ms", type=float, default=0.0)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--vus", type=int, default=1)
    parser.add_argument("--fail-rate", type=float, default=0.0)
    parser.add_argument(
        "--pass",
        dest="passed",
        action="store_true",
        help="Mark the test row as passed.",
    )
    parser.add_argument("--error-message", default="")
    parser.add_argument("--port", type=int, default=0, help="Required for --kind service.")
    parser.add_argument("--up", action="store_true", help="Service probe succeeded.")
    parser.add_argument("--latency-ms", type=float, default=0.0)
    return parser


def row_from_args(args: argparse.Namespace) -> tuple[str, dict]:
    """Build a serializable dict from parsed args. Raises on missing fields."""
    if args.kind == "service":
        if args.port <= 0:
            raise ValueError("--port is required and must be > 0 for --kind service")
        row = ServiceRunRow(
            language=args.language,
            port=args.port,
            up=bool(args.up),
            latency_ms=args.latency_ms,
            error_message=args.error_message,
        )
        return args.kind, row.to_history_dict()

    if not args.test_name:
        raise ValueError("--test-name is required for manual|automated|performance")
    test_type = args.test_type or args.kind
    row = ResultRow(
        test_name=args.test_name,
        test_type=test_type,
        language=args.language,
        p90_ms=args.p90_ms,
        p95_ms=args.p95_ms,
        p98_ms=args.p98_ms,
        p99_ms=args.p99_ms,
        ttl_ms=args.ttl_ms,
        p50_ms=args.p50_ms,
        avg_ms=args.avg_ms,
        max_ms=args.max_ms,
        iterations=args.iterations,
        vus=args.vus,
        fail_rate=args.fail_rate,
        passed=bool(args.passed),
        error_message=args.error_message,
    )
    return args.kind, row.to_history_dict()


def main(argv: list[str] | None = None) -> int:
    """Parse CLI, append one row, print the target paths. Return process exit."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        kind, payload = row_from_args(args)
        csv_path, jsonl_path = append_history(kind, payload)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"appended {kind} -> {csv_path}")
    print(f"appended {kind} -> {jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
