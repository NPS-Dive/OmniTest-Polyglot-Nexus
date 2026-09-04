# TS-FUNC-003 — SearchByVector

| Field | Value |
|-------|--------|
| Identifier | TS-FUNC-003 |
| Title | SearchByVector returns L2 neighbours |
| Test basis | `VectorSearchRequest`; HNSW `vector_l2_ops` |
| Priority | High |
| Technique hint | Happy path + BVA on `top_k` (0 / huge) |
| OWASP links | API4 via `TC-SEC-API4-vector-topk` + `TC-EDGE-003` |
| Realizing cases | `TC-FUNC-003.md`, `TC-EDGE-003.md`, `TC-SEC-API4-vector-topk.md` |
| BDD | `docs/gherkin/person-vector.feature` |
| Note | NULL embeddings → empty page is environment, not mapping defect |

**Condition:** L2 nearest neighbours for a 384-dim vector. `top_k=0` clamps or rejects; extreme `top_k` does not crash.
