# Vector store (PostgreSQL + pgvector)

## Responsibility

SQL that creates **one `persons_*` table per language** inside a single database `opn_db`. Isolation is by table, not by database, so k6 can hit all six gRPC APIs at once without one heap becoming the bottleneck.

## Canonical columns

| Column | Notes |
|--------|--------|
| `id` | UUID PK (same ids across tables after seed) |
| `first_name`, `last_name`, `age` | Identity |
| `sex`, `marital_status`, `living_place`, `occupation` | VARCHAR. Seed CSV uses lowercase labels (`male`, `job seeker`). APIs map to proto enums. |
| `national_code` | 10 digits |
| `embedding` | `vector(384)`, L2 / `<->` / `vector_l2_ops` |
| `has_passport` | `BOOLEAN DEFAULT FALSE` (proto field; not in CSV) |

`birth_date` is **not** stored. APIs derive an approximate ISO date from `age`.

## Init scripts (fresh Docker volume only)

Docker Compose mounts this folder to `/docker-entrypoint-initdb.d` and the CSV to `/master_seed.csv`.

| File | Role |
|------|------|
| `01_init_extensions.sql` | `CREATE EXTENSION vector` |
| `02_create_tables.sql` | Six tables including `persons_golang` |
| `03_seed_data.sql` | Server `COPY` from `/master_seed.csv` into all six |
| `04_create_indexes.sql` | B-tree + HNSW after COPY |
| `05_align_optional_columns.sql` | `has_passport` on older tables (`IF NOT EXISTS`) |

Changing these files does **not** re-run on an existing `pg_data` volume.

## Existing volume (do not wipe embeddings)

```powershell
# Add persons_golang
Get-Content data/vector-store/migrations/migrate_add_golang.sql | docker exec -i opn-postgres psql -U opn_admin -d opn_db

# Seed golang only (CSV must be mounted at /master_seed.csv)
Get-Content data/vector-store/migrations/seed_golang_only.sql | docker exec -i opn-postgres psql -U opn_admin -d opn_db

# has_passport on older tables
Get-Content data/vector-store/05_align_optional_columns.sql | docker exec -i opn-postgres psql -U opn_admin -d opn_db
```

Then backfill NULL embeddings only:

```powershell
python data/mock-generator/embedding_updater.py --tables persons_golang
```

`VACUUM ANALYZE` runs automatically after a non-empty update.

## Nested `migrations/`

Postgres docker entrypoint executes `*.sql` in the **top** of `initdb.d`, not subfolders. `migrations/` is for operator-run scripts only.
