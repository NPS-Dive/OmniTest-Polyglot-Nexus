<!--
File: services/ai-agents/hermes/skills.md
Purpose: Hermes Agent skills that wrap OmniTest MCP + LangGraph. Hermes owns
         long-term memory (past runs, which language was slow, prior bugs).
-->

# Hermes skills (OmniTest)

Hermes is the **execution teammate**, not “an LLM name”. Skills should be repeatable.

## Memory notes (QAQC)

Store: last `test_name` + `language` + `p95_ms` + pass/fail; BUG ids; which table lacked embeddings. Do not store OpenClaw channel tokens.

## Skill: compare languages

1. MCP `read_last_report`
2. LangGraph `run_comparison`
3. Reply with rank + caveat if n=0

## Skill: explain a fail

1. MCP `read_last_report` or `run_test` if the user asked to reproduce
2. LangGraph `explain_failure`
3. If product bug: `draft_istqb_bug` then tell the user to copy TEMPLATE.md

## Skill: rag then optionally run

1. `ai-gateway` POST `/rag/query` **or** LangGraph `rag_ask`
2. Heavy “run TC-FUNC-001 on all langs” → MCP `run_test` in a loop (or orchestrator `/tests/run-all`)

## Skill: CreatePerson (write)

Read-mostly default. `grpc_call` is a stub. Only insert after an explicit user confirmation interrupt. Prefer `Invoke-FunctionalRpc.ps1 -Rpc CreatePerson` via `run_test` / TC-FUNC-004, not raw SQL.

## Sandbox

Run delegated PowerShell/k6 inside Hermes’ sandbox when available. Keep Hermes ports on `127.0.0.1`.
