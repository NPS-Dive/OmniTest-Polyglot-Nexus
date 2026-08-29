# ==============================================================================
# File: services/ai-gateway/main.py
# Purpose: FastAPI RAG + agent HTTP for Hermes / Blazor. Not a second chatbot.
#          Routes: /health, /rag/query, /agent/run
# SOLID: SRP — HTTP + local markdown retrieval. Heavy graphs live in ai-agents.
# Dependencies: data/knowledge-base/*.md ; optional POST to LangGraph stubs.
# ==============================================================================
"""ai-gateway composition root."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

GATEWAY_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATEWAY_DIR.parent.parent
KB_DIR = REPO_ROOT / "data" / "knowledge-base"

app = FastAPI(title="OmniTest AI gateway", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5080", "http://127.0.0.1:5080"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RagQuery(BaseModel):
    """Natural-language question over knowledge-base markdown."""

    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=12)


class AgentRun(BaseModel):
    """Forward a heavy task name to LangGraph stubs (no LLM required)."""

    task: str = Field(description="run_comparison|explain_failure|draft_istqb_bug|rag_ask")
    payload: dict[str, Any] = Field(default_factory=dict)


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def _load_kb() -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    if not KB_DIR.is_dir():
        return docs
    for path in sorted(KB_DIR.glob("*.md")):
        docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "kb": str(KB_DIR)}


@app.post("/rag/query")
def rag_query(body: RagQuery) -> dict[str, Any]:
    """Keyword overlap over knowledge-base files (deterministic, no embeddings)."""
    q = _tokenize(body.question)
    scored: list[dict[str, Any]] = []
    for name, text in _load_kb():
        tokens = _tokenize(text)
        hit = len(q & tokens)
        if hit == 0:
            continue
        snippet = text[:600].replace("\n", " ")
        scored.append({"source": name, "score": hit, "snippet": snippet})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "question": body.question,
        "matches": scored[: body.top_k],
        "note": "Lexical overlap only. Person-table vectors are queried via gRPC SearchByVector, not this endpoint.",
    }


@app.post("/agent/run")
def agent_run(body: AgentRun) -> dict[str, Any]:
    """
    Invoke LangGraph stub functions in-process when importable.
    OpenClaw must not call this for light Q&A — Hermes does.
    """
    try:
        from graphs import (  # type: ignore
            draft_istqb_bug,
            explain_failure,
            rag_ask,
            run_comparison,
        )
    except ImportError:
        # graphs.py lives under services/ai-agents/langgraph — add that dir to PYTHONPATH
        import sys

        lg = REPO_ROOT / "services" / "ai-agents" / "langgraph"
        sys.path.insert(0, str(lg))
        from graphs import draft_istqb_bug, explain_failure, rag_ask, run_comparison

    fn = {
        "run_comparison": run_comparison,
        "explain_failure": explain_failure,
        "draft_istqb_bug": draft_istqb_bug,
        "rag_ask": rag_ask,
    }.get(body.task)
    if fn is None:
        return {"ok": False, "error": f"unknown task {body.task}"}
    return {"ok": True, "task": body.task, "result": fn(body.payload)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5082, reload=False)
