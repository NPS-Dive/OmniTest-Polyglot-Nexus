# Existing-volume migrations

## Purpose

Docker init (`01_`–`05_` in the parent folder) runs **only on first Postgres start**. If `pg_data` already exists, run these scripts by hand. Do not wipe the volume — that would drop existing embeddings.

## Scripts

| File | When |
|------|------|
| `migrate_add_golang.sql` | Add `persons_golang` + indexes |
| `seed_golang_only.sql` | `COPY` `master_seed.csv` into `persons_golang` only |

`has_passport` on older tables: run parent `05_align_optional_columns.sql`.

## Example (container `opn-postgres` up)

```powershell
Get-Content data/vector-store/migrations/migrate_add_golang.sql | docker exec -i opn-postgres psql -U opn_admin -d opn_db
Get-Content data/vector-store/migrations/seed_golang_only.sql | docker exec -i opn-postgres psql -U opn_admin -d opn_db
```

Then: `python data/mock-generator/embedding_updater.py --tables persons_golang`
