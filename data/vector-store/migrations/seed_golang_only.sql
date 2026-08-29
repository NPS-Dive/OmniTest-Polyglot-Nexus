-- ==============================================================================
-- File: migrations/seed_golang_only.sql
-- Purpose: COPY master_seed.csv into persons_golang only (existing volume).
-- Requires: migrate_add_golang.sql applied; CSV mounted at /master_seed.csv.
-- Fails on PK conflict if the table is already seeded — that is intentional.
-- SOLID: SRP — one-table seed. Embeddings stay NULL until embedding_updater.py.
-- ==============================================================================

COPY persons_golang (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);
