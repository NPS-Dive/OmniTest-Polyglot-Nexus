# BUG-&lt;id&gt; — &lt;short title&gt;

<!--
File: apps/benchmark-runner/reports/bugs/TEMPLATE.md
Purpose: ISTQB-aligned defect report. Copy to BUG-001.md (do not edit the template in place for a real bug).
SOLID: SRP — one defect, one file.
-->

| Field | Value |
|-------|--------|
| **Identifier** | BUG-NNN |
| **Title** | |
| **Severity** | Blocker / Critical / Major / Minor / Trivial |
| **Priority** | High / Medium / Low |
| **Environment** | Windows, compose stack, API version / commit |
| **Module / language** | grpc-cpp / grpc-python / grpc-java / grpc-go / grpc-csharp / grpc-node |
| **Table** | persons_* |
| **Test id** | TC-FUNC-00N / k6 profile |
| **BDD ref** | `docs/gherkin/….feature` |

## Precondition

What must already be running (Postgres, which APIs, seed present).

## Steps to reproduce

1.
2.
3.

## Expected result

Contract from `shared/proto/person_service.proto` and the language README.

## Actual result

Including gRPC status and a short message.

## Evidence

- CLI / grpcurl snippet
- CSV/JSONL row (`timestamp_utc`, `test_name`)
- Grafana panel or Tempo trace id if available

## Isolation

Which of the six languages **fail** the same TestId? Which **pass**? (Fair comparison requires the same payload.)

## Suggestion

Likely layer (presentation mapping vs repository SQL vs clamp rules) and a non-breaking fix direction.
