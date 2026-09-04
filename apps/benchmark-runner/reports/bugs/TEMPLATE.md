# BUG-&lt;id&gt; — &lt;short title&gt;

<!--
File: apps/benchmark-runner/reports/bugs/TEMPLATE.md
Purpose: Defect report for dynamic testing per ISTQB CTFL 4.0.1 §5.5
         (ASTQB uses the same syllabus; no extra US-only form).
SOLID: SRP — one anomaly, one file. Copy to BUG-001.md; do not edit this
       template in place for a real defect.
-->

## Identification

| Field | Value |
|-------|--------|
| **Identifier** | BUG-NNN (never reuse) |
| **Title** | Short summary of the *anomaly* (observable), not a guessed root cause |
| **Date observed (UTC)** | YYYY-MM-DDThh:mm:ssZ |
| **Author / role** | Name — Tester |
| **Organization** | OmniTest-Polyglot-Nexus (local demo) |
| **Status** | Open / Deferred / Duplicate / Waiting to be fixed / Awaiting confirmation testing / Re-opened / Closed / Rejected |
| **SDLC phase / activity** | Dynamic system test (API) |

## Test object and environment

| Field | Value |
|-------|--------|
| **Test object** | PersonService / language folder / table |
| **Module / language** | grpc-cpp / grpc-python / grpc-java / grpc-go / grpc-csharp / grpc-node |
| **Table** | persons_* |
| **Environment** | OS, Docker/compose, API start command, commit SHA if known |
| **Build / version** | |

## Context (how it was found)

| Field | Value |
|-------|--------|
| **Test case** | TC-FUNC-00N / TC-EDGE-00N / TC-PERF-00N / TC-SEC-001 |
| **Test scenario** | TS-* |
| **BDD ref** | `docs/gherkin/….feature` |
| **Technique / data** | EP / BVA / k6 profile / payload kind |
| **History row** | `timestamp_utc` + `test_name` in reports/history |

## Description of the failure

### Preconditions

What must already be running (Postgres, which APIs, seed / embeddings).

### Steps to reproduce

1.
2.
3.

### Expected results

Contract from `shared/proto/person_service.proto` and the test case.

### Actual results

gRPC status, message, and behaviour.

### Evidence

- CLI / grpcurl / k6 snippet
- CSV/JSONL row
- Grafana panel or Tempo trace id (if collector is up)
- Optional screenshot of Blazor Compare

## Classification

| Field | Value |
|-------|--------|
| **Severity** | Blocker / Critical / Major / Minor / Trivial — *impact on stakeholders or requirements* (CTFL) |
| **Priority** | High / Medium / Low — *order to fix for fair comparison / demo* |
| **Isolation** | Which of the six languages fail the same TC? Which pass? Same payload required. |

### Severity guide (this repo)

| Severity | Use when |
|----------|----------|
| Blocker | Language API will not start or accept any RPC |
| Critical | Wrong table, data loss, or SQL injection executed |
| Major | Wrong proto/SQL mapping, `total_count` unfair, enum write drift |
| Minor | Clamp/docs mismatch, noisy error text |
| Trivial | Cosmetic message / log only |

## Suggestion

Likely layer (presentation mapper vs repository SQL vs clamp) and a non-breaking fix direction.

## Lifecycle log

| When (UTC) | Status | Note |
|------------|--------|------|
| | Open | Logged from test execution |
| | | Confirmation test TC-… on languages: |
