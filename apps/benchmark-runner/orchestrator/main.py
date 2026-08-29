# ==============================================================================
# File: apps/benchmark-runner/orchestrator/main.py
# Purpose: HTTP façade so Blazor WASM can trigger tests and read reports
#          (browsers cannot spawn PowerShell). Port 5081.
# SOLID: SRP — process spawn + file/TCP status. No Person SQL here.
# Dependencies: FastAPI, config/services.json, powershell/Invoke-*.ps1
# ==============================================================================
"""Benchmark orchestrator — composition root for the HTTP API."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- paths (this file lives in apps/benchmark-runner/orchestrator) ---
ORCH_DIR = Path(__file__).resolve().parent
RUNNER_DIR = ORCH_DIR.parent
REPO_ROOT = RUNNER_DIR.parent.parent
SERVICES_JSON = RUNNER_DIR / "config" / "services.json"
PS_DIR = RUNNER_DIR / "powershell"
HISTORY_DIR = RUNNER_DIR / "reports" / "history"

app = FastAPI(
    title="OmniTest benchmark orchestrator",
    version="1.0.0",
    description="Trigger PowerShell tests and expose latest JSONL rows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5080",
        "http://127.0.0.1:5080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunTestBody(BaseModel):
    """POST /tests/run payload."""

    test_id: str = Field(alias="testId", description="Catalog id, e.g. TC-FUNC-001")
    language: str = Field(description="cpp|python|java|go|csharp|node")

    model_config = {"populate_by_name": True}


class ProbeBody(BaseModel):
    """Optional probe helper used by the Blazor Probe page."""

    language: str
    rpc: Literal["CreatePerson", "ReadAllPersons", "SearchByFilter", "SearchByVector"]


def _load_services() -> dict[str, Any]:
    if not SERVICES_JSON.is_file():
        raise HTTPException(500, f"missing {SERVICES_JSON}")
    return json.loads(SERVICES_JSON.read_text(encoding="utf-8"))


def _powershell() -> str:
    exe = shutil.which("pwsh") or shutil.which("powershell")
    if not exe:
        raise HTTPException(500, "Neither pwsh nor powershell is on PATH")
    return exe


def _run_ps(script: Path, args: list[str], timeout: int = 120) -> dict[str, Any]:
    if not script.is_file():
        raise HTTPException(500, f"missing script {script}")
    cmd = [_powershell(), "-NoProfile", "-File", str(script), *args]
    proc = subprocess.run(
        cmd,
        cwd=str(PS_DIR),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-4000:],
        "ok": proc.returncode == 0,
    }


def _tail_jsonl(path: Path, n: int = 20) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    out: list[dict[str, Any]] = []
    for ln in lines[-n:]:
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            out.append({"raw": ln})
    return out


def _tcp_up(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness for compose / Blazor."""
    return {"status": "ok"}


@app.get("/services/status")
def services_status() -> dict[str, Any]:
    """TCP probe of each language port from services.json (not a gRPC handshake)."""
    cfg = _load_services()
    items = []
    for key, meta in cfg.get("languages", {}).items():
        host = meta["host"]
        port = int(meta["port"])
        items.append(
            {
                "language": key,
                "host": host,
                "port": port,
                "table": meta.get("table"),
                "up": _tcp_up(host, port),
            }
        )
    return {"services": items}


@app.get("/reports/latest")
def reports_latest(limit: int = 30) -> dict[str, Any]:
    """Last JSONL objects from each history file (empty arrays if never run)."""
    return {
        "manual": _tail_jsonl(HISTORY_DIR / "manual_results.jsonl", limit),
        "automated": _tail_jsonl(HISTORY_DIR / "automated_results.jsonl", limit),
        "performance": _tail_jsonl(HISTORY_DIR / "performance_results.jsonl", limit),
    }


@app.post("/tests/run")
def tests_run(body: RunTestBody) -> dict[str, Any]:
    """Run one catalogued test via Invoke-ManualTest.ps1."""
    script = PS_DIR / "Invoke-ManualTest.ps1"
    return _run_ps(script, ["-TestId", body.test_id, "-Language", body.language])


@app.post("/tests/run-all")
def tests_run_all() -> dict[str, Any]:
    """Run the full manual loop (can take minutes if every API is up)."""
    script = PS_DIR / "Invoke-AllManualTests.ps1"
    return _run_ps(script, [], timeout=900)


@app.post("/probe")
def probe(body: ProbeBody) -> dict[str, Any]:
    """Direct RPC via Invoke-FunctionalRpc.ps1 for the Blazor Probe page."""
    kind = {
        "CreatePerson": "create_minimal",
        "ReadAllPersons": "readall_default",
        "SearchByFilter": "filter_name",
        "SearchByVector": "vector_dummy",
    }[body.rpc]
    script = PS_DIR / "Invoke-FunctionalRpc.ps1"
    return _run_ps(
        script,
        [
            "-Language",
            body.language,
            "-Rpc",
            body.rpc,
            "-PayloadKind",
            kind,
            "-TestType",
            "manual",
        ],
    )


if __name__ == "__main__":
    # Composition root: bind 5081 on all interfaces so WASM on 5080 can reach us.
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5081, reload=False)
    sys.exit(0)
