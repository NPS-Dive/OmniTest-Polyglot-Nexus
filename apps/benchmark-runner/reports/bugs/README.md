# Defect reports (ISTQB CTFL 4.0.1 §5.5 / ASTQB)

ASTQB (US ISTQB board) uses **the same** CTFL 4.0.1 defect content. A report from dynamic testing must be complete enough to **reproduce and resolve** the anomaly.

## When to open a file

| Situation | Action |
|-----------|--------|
| Catalogued TC failed after a **real** RPC/k6 call | Copy [TEMPLATE.md](TEMPLATE.md) → `BUG-NNN.md`. Add a register row. |
| `grpcurl` / k6 / API missing | History row only. **Environment block** — not a product defect. |
| Same failure already logged | Status **Duplicate**; point at the original id. |
| Anomaly is a testware/threshold issue | Still a defect in *testware*; log it, mark test object = k6/script. |

Never reuse an identifier. Never overwrite history CSV/JSONL to “clear” a bug.

## Status values (CTFL examples)

`Open` → `Waiting to be fixed` → `Awaiting confirmation testing` → `Closed`  
Also: `Deferred`, `Duplicate`, `Re-opened`, `Rejected`.

Confirmation testing = re-run the **same TC** on the failing language **and** isolation languages.

## Folder

| File | Role |
|------|------|
| [TEMPLATE.md](TEMPLATE.md) | Blank CTFL field set |
| [register.md](register.md) | Defect register (monitoring work product) |
| [BUG-001.md](BUG-001.md) | Closed — `persons_golang` missing on existing volume |
| [BUG-002.md](BUG-002.md) | Closed — C# mapper `Person` name clash |

## Related

- Scenarios / cases: [docs/qa/](../../../../docs/qa/)
- RAG: [data/knowledge-base/istqb-defect-process.md](../../../../data/knowledge-base/istqb-defect-process.md)
