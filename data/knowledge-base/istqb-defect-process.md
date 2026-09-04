<!--
File: data/knowledge-base/istqb-defect-process.md
Purpose: RAG-ready defect workflow — ISTQB CTFL 4.0.1 §5.5 / ASTQB (same syllabus).
-->

# ISTQB / ASTQB defect process (this repo)

Syllabus: ISTQB CTFL **v4.0.1** (15 Sep 2024). ASTQB is the US member board; it does not define a second form.

A defect is logged when a catalogued test fails **after** a real RPC or k6 call (or static analysis / compile blocks the test object). A grpcurl-missing skip is an **environment block**, not a product bug — still record it in CSV, but do not open `BUG-NNN` unless the API itself failed.

## Testware map

| CTFL work product | Path |
|-------------------|------|
| Test conditions (scenarios) | `docs/qa/scenarios/TS-*/00-scenario.md` |
| Test cases | `docs/qa/scenarios/TS-*/TC-*.md` (see `docs/qa/catalog.md`) |
| Test procedures | PowerShell + k6 |
| Test logs | `apps/benchmark-runner/reports/history/` |
| Defect reports | `apps/benchmark-runner/reports/bugs/BUG-*.md` |
| Defect register | `apps/benchmark-runner/reports/bugs/register.md` |

## Fields (copy `apps/benchmark-runner/reports/bugs/TEMPLATE.md`)

CTFL §5.5 typical content for a dynamic-testing report:

- Unique identifier, title, date, author/role, organization
- Test object and test environment
- Context (test case, activity, technique, data)
- Steps, expected vs actual, evidence (logs, dumps)
- Severity (impact), priority (order to fix), status
- References to the test case

Repo extras (fair comparison): isolation across six languages; suggestion of layer (mapper vs SQL vs clamp).

## Status

Open, Deferred, Duplicate, Waiting to be fixed, Awaiting confirmation testing, Re-opened, Closed, Rejected.

## After every run

1. CLI table (PowerShell runners).
2. Managerial markdown/HTML via `New-ManagerialReport.ps1`.
3. On product failure: new `BUG-<id>.md` + register row. Do not overwrite history files.

## Fair comparison rule

Rank languages only on the **same TC, same payload, same machine**.
