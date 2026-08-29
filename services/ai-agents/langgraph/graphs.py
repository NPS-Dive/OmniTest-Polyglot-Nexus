# ==============================================================================
# File: services/ai-agents/langgraph/graphs.py
# Purpose: Deterministic QA graphs invoked as Hermes skills (not a user chat).
#          Stubs return structured dicts so wiring can be completed later.
# SOLID: OCP — add a graph function; OpenClaw never imports this module.
# Graphs: run_comparison, explain_failure, draft_istqb_bug, rag_ask
# ==============================================================================
"""LangGraph-shaped stubs (no LangGraph runtime required for scaffolding)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
HISTORY = REPO / "apps" / "benchmark-runner" / "reports" / "history"
KB = REPO / "data" / "knowledge-base"


def run_comparison(payload: dict[str, Any]) -> dict[str, Any]:
    """Rank languages from the last performance/manual JSONL rows."""
    rows = _tail_jsonl(HISTORY / "manual_results.jsonl") + _tail_jsonl(
        HISTORY / "performance_results.jsonl"
    )
    by_lang: dict[str, list[float]] = {}
    for row in rows:
        lang = str(row.get("language", ""))
        try:
            p95 = float(row.get("p95_ms") or 0)
        except (TypeError, ValueError):
            continue
        by_lang.setdefault(lang, []).append(p95)
    means = {k: (sum(v) / len(v) if v else None) for k, v in by_lang.items()}
    ranked = sorted(
        ((k, m) for k, m in means.items() if m is not None),
        key=lambda kv: kv[1],
    )
    return {
        "graph": "run_comparison",
        "payload": payload,
        "mean_p95_ms": means,
        "rank_fastest_first": [k for k, _ in ranked],
        "note": "Stub uses existing history only. Empty history → empty rank.",
    }


def explain_failure(payload: dict[str, Any]) -> dict[str, Any]:
    """Explain the latest failing row (or the test_name in payload)."""
    rows = _tail_jsonl(HISTORY / "manual_results.jsonl") + _tail_jsonl(
        HISTORY / "automated_results.jsonl"
    )
    target = payload.get("test_name")
    fail = None
    for row in reversed(rows):
        passed = row.get("pass") in (True, "True", "true")
        if passed:
            continue
        if target and row.get("test_name") != target:
            continue
        fail = row
        break
    return {
        "graph": "explain_failure",
        "failure": fail,
        "hints": [
            "If error_message mentions grpcurl, this is an environment skip.",
            "If Unavailable/connection refused, start that language API.",
            "If proto/SQL mapping errors, check the language README.",
        ],
    }


def draft_istqb_bug(payload: dict[str, Any]) -> dict[str, Any]:
    """Fill TEMPLATE.md fields from a failure row (does not write BUG-NNN)."""
    explained = explain_failure(payload)
    fail = explained.get("failure") or {}
    return {
        "graph": "draft_istqb_bug",
        "suggested_title": fail.get("test_name") or "Untitled failure",
        "severity": "Major",
        "module_language": fail.get("language"),
        "evidence": fail,
        "template": str(REPO / "apps" / "benchmark-runner" / "reports" / "bugs" / "TEMPLATE.md"),
        "isolation": "Re-run the same TestId on the other five languages.",
    }


def rag_ask(payload: dict[str, Any]) -> dict[str, Any]:
    """Keyword scan of knowledge-base (same idea as ai-gateway /rag/query)."""
    q = str(payload.get("question") or payload.get("message") or "").lower()
    hits = []
    if KB.is_dir():
        for path in KB.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            if q and any(tok in text.lower() for tok in q.split() if len(tok) > 3):
                hits.append({"source": path.name, "snippet": text[:400]})
    return {"graph": "rag_ask", "question": q, "hits": hits[:5]}


def _tail_jsonl(path: Path, n: int = 50) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out = []
    for ln in path.read_text(encoding="utf-8").splitlines()[-n:]:
        if not ln.strip():
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return out
