# Mock generator

SOLID reference module for this monorepo: one job per file, exporter behind an interface, orchestrator as composition root.

| File | Principle | Job |
|------|-----------|-----|
| `models.py` | SRP | `PersonModel` DTO only |
| `rules.py` | SRP | 10-digit national code, max two identical consecutive digits |
| `factory.py` | SRP | Faker assembly |
| `exporters.py` | OCP / DIP | `BaseExporter` + `CsvExporter` |
| `main.py` | Composition root | Wires factory + exporter → `data/master_seed.csv` |
| `embedding_updater.py` | SRP / DIP | Backfill `embedding` where NULL; skip existing vectors |

## Generate CSV (only if you intend to replace 1M rows)

```powershell
pip install -r data/mock-generator/requirements.txt
python data/mock-generator/main.py
```

Do **not** regenerate the CSV just to add Golang. The same file is `COPY`'d into every `persons_*` table.

## Embeddings

Model: `all-MiniLM-L6-v2` (384 dimensions). Connection default: `postgresql://opn_admin:opn_secret@localhost:5432/opn_db`.

```powershell
# All six tables; already-embedded rows are skipped
python data/mock-generator/embedding_updater.py

# New table only (after migrate + seed)
python data/mock-generator/embedding_updater.py --tables persons_golang

# Smoke (100 rows)
python data/mock-generator/embedding_updater.py --tables persons_golang --max-records 100
```

After a large UPDATE the script runs `VACUUM ANALYZE` on that table.

## Seed label vs proto enum

CSV values are lowercase (`male`, `full-time`). gRPC proto enums are `SEX_MALE`, `OCCUPATION_FULL_TIME`. Mapping is the API layer's job — this folder does not rewrite 1M rows.
