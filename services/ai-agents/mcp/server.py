# ==============================================================================
# File: services/ai-agents/mcp/server.py
# Purpose: OmniTest MCP tool bus (stdio-friendly). Shared by Hermes; OpenClaw
#          uses ask_hermes / delegate, not a second copy of these tools.
# SOLID: SRP per tool. SQL tool is SELECT-only.
# Tools: list_services, grpc_call (stub), run_test, read_last_report,
#        query_persons_sql_readonly
# ==============================================================================
"""Minimal MCP-style server: JSON-RPC-ish over stdin/stdout or `python server.py --demo`."""

from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AGENTS = HERE.parent
REPO = AGENTS.parent.parent
SERVICES = REPO / "apps" / "benchmark-runner" / "config" / "services.json"
PS_MANUAL = REPO / "apps" / "benchmark-runner" / "powershell" / "Invoke-ManualTest.ps1"
HISTORY = REPO / "apps" / "benchmark-runner" / "reports" / "history"

_SELECT_ONLY = re.compile(r"^\s*select\b", re.IGNORECASE | re.DOTALL)
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|execute)\b",
    re.IGNORECASE,
)


def list_services(_: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return language → host:port from services.json plus TCP up/down."""
    cfg = json.loads(SERVICES.read_text(encoding="utf-8"))
    rows = []
    for key, meta in cfg.get("languages", {}).items():
        up = False
        try:
            with socket.create_connection((meta["host"], int(meta["port"])), timeout=0.3):
                up = True
        except OSError:
            up = False
        rows.append({**meta, "language": key, "up": up})
    return {"services": rows}


def grpc_call(args: dict[str, Any]) -> dict[str, Any]:
    """
    Stub: does not send gRPC. Hermes must confirm CreatePerson before a future
    implementation wires grpcurl. Read-mostly by default.
    """
    return {
        "ok": False,
        "stub": True,
        "message": "grpc_call is a stub. Use run_test or the PowerShell runner. CreatePerson requires explicit confirmation in a Hermes skill.",
        "requested": args,
    }


def run_test(args: dict[str, Any]) -> dict[str, Any]:
    """Spawn Invoke-ManualTest.ps1 (Windows)."""
    test_id = args.get("testId") or args.get("test_id")
    language = args.get("language")
    if not test_id or not language:
        return {"ok": False, "error": "testId and language are required"}
    ps = "pwsh" if _which("pwsh") else "powershell"
    if not _which(ps):
        return {"ok": False, "error": "PowerShell not found"}
    proc = subprocess.run(
        [ps, "-NoProfile", "-File", str(PS_MANUAL), "-TestId", str(test_id), "-Language", str(language)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-2000:],
    }


def read_last_report(args: dict[str, Any] | None = None) -> dict[str, Any]:
    """Tail JSONL history files."""
    n = int((args or {}).get("limit", 10))
    out: dict[str, Any] = {}
    for stem in ("manual_results", "automated_results", "performance_results"):
        path = HISTORY / f"{stem}.jsonl"
        if not path.is_file():
            out[stem] = []
            continue
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        parsed = []
        for ln in lines[-n:]:
            try:
                parsed.append(json.loads(ln))
            except json.JSONDecodeError:
                parsed.append({"raw": ln})
        out[stem] = parsed
    return out


def query_persons_sql_readonly(args: dict[str, Any]) -> dict[str, Any]:
    """
    SELECT only against opn_db. Rejects anything that is not a single SELECT
    (including comments that hide DML). Optional psycopg if installed.
    """
    sql = (args.get("sql") or "").strip()
    if not sql:
        return {"ok": False, "error": "sql is required"}
    if ";" in sql.rstrip().rstrip(";"):
        return {"ok": False, "error": "multiple statements rejected"}
    if not _SELECT_ONLY.match(sql) or _FORBIDDEN.search(sql):
        return {"ok": False, "error": "rejected: SELECT only"}
    try:
        import psycopg2  # type: ignore
    except ImportError:
        return {
            "ok": False,
            "error": "psycopg2 not installed; query was validated as SELECT-only but not executed",
            "sql": sql,
        }
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="opn_db",
        user="opn_admin",
        password="opn_secret",
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(50)
        return {"ok": True, "columns": cols, "rows": rows}
    finally:
        conn.close()


def _which(name: str) -> bool:
    from shutil import which

    return which(name) is not None


TOOLS = {
    "list_services": list_services,
    "grpc_call": grpc_call,
    "run_test": run_test,
    "read_last_report": read_last_report,
    "query_persons_sql_readonly": query_persons_sql_readonly,
}


def dispatch(name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    fn = TOOLS.get(name)
    if not fn:
        return {"ok": False, "error": f"unknown tool {name}"}
    return fn(args or {})


def main() -> None:
    parser = argparse.ArgumentParser(description="OmniTest MCP tool server (demo CLI).")
    parser.add_argument("--demo", action="store_true", help="Print list_services and exit")
    parser.add_argument("--tool", help="Tool name")
    parser.add_argument("--args", default="{}", help="JSON object")
    ns = parser.parse_args()
    if ns.demo:
        print(json.dumps(list_services(), indent=2))
        return
    if ns.tool:
        print(json.dumps(dispatch(ns.tool, json.loads(ns.args)), indent=2, default=str))
        return
    # stdio loop: one JSON line { "tool": "...", "args": {} } per request
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        result = dispatch(msg.get("tool", ""), msg.get("args") or {})
        sys.stdout.write(json.dumps(result, default=str) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
