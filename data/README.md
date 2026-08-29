# data

| Path | Role |
|------|------|
| `master_seed.csv` | ~1M shared seed rows (COPY into all `persons_*`) |
| `vector-store/` | Init SQL + migrations (do not wipe `pg_data` lightly) |
| `mock-generator/` | Faker CSV + embedding backfill |
| `knowledge-base/` | RAG markdown for ai-gateway / Hermes |
