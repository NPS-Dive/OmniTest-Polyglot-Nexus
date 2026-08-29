<!--
File: data/knowledge-base/istqb-defect-process.md
Purpose: RAG-ready defect workflow aligned with ISTQB Foundation fields.
-->

# ISTQB defect process (this repo)

A defect is logged when a catalogued test fails **after** a real RPC (or when an API is down when it should be up). A grpcurl-missing skip is an **environment block**, not a product bug — still record it in CSV, but do not open BUG-NNN unless the API itself failed.

## Fields (copy `apps/benchmark-runner/reports/bugs/TEMPLATE.md`)

| Field | Meaning here |
|-------|----------------|
| Identifier | `BUG-001` increment; never reuse |
| Title | Observable failure, not a guess |
| Severity | Blocker (no service), Critical (wrong table / data loss), Major (wrong mapping), Minor (clamp docs), Trivial (message text) |
| Priority | Business order for fixing comparison fairness |
| Environment | OS, compose up?, which APIs, commit |
| Module / language | One of six; fill Isolation with the others |
| Precondition / steps / expected / actual | Required |
| Evidence | `timestamp_utc` + `test_name` in history CSV/JSONL |
| Isolation | Same TestId on the other five languages |
| Suggestion | Layer (mapper vs SQL vs clamp) |

## After every run

1. CLI table (built into the PowerShell runners).
2. Managerial markdown/HTML via `New-ManagerialReport.ps1` (cross-language means).
3. On product failure: new `BUG-<id>.md`. Do not overwrite history files.

## Fair comparison rule

Rank languages only on the **same RPC, same payload, same machine**. A CreatePerson on C# is not comparable to ReadAll on Go.
