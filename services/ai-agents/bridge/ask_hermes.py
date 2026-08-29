# ==============================================================================
# File: services/ai-agents/bridge/ask_hermes.py
# Purpose: First-party OpenClaw → Hermes forwarder. Minimal payload only:
#          user id + current message + channel context. No OpenClaw history dump.
# SOLID: SRP — HTTP bridge. Does not own memory or run LangGraph itself.
# ==============================================================================
"""POST a heavy task to Hermes Agent (or print the payload if HERMES_BASE_URL is unset)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


def build_payload(user_id: str, message: str, channel: str) -> dict[str, Any]:
    """Contract: do not attach OpenClaw session transcripts."""
    return {
        "user_id": user_id,
        "message": message,
        "channel": channel,
        "source": "openclaw",
        "routing": "heavy",
    }


def ask_hermes(user_id: str, message: str, channel: str = "cli") -> dict[str, Any]:
    body = build_payload(user_id, message, channel)
    base = os.environ.get("HERMES_BASE_URL", "").rstrip("/")
    if not base:
        return {
            "ok": False,
            "relayed": False,
            "reason": "HERMES_BASE_URL unset — payload not sent",
            "payload": body,
        }
    url = f"{base}/v1/chat"  # product-specific; override with HERMES_CHAT_PATH
    path = os.environ.get("HERMES_CHAT_PATH", "/v1/chat")
    url = f"{base}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"text": raw}
            return {"ok": True, "relayed": True, "hermes": parsed}
    except urllib.error.URLError as exc:
        return {"ok": False, "relayed": False, "error": str(exc), "payload": body}


def main() -> None:
    p = argparse.ArgumentParser(description="Forward one heavy turn to Hermes.")
    p.add_argument("--user-id", default="local")
    p.add_argument("--channel", default="cli")
    p.add_argument("message", nargs="+")
    ns = p.parse_args()
    result = ask_hermes(ns.user_id, " ".join(ns.message), ns.channel)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
