-- ==============================================================================
-- File: migrations/migrate_add_golang.sql
-- Purpose: Apply persons_golang to an ALREADY-INITIALIZED Docker volume.
-- Why this folder: NOT mounted as a standalone extra, but sibling of 01-05.
-- IMPORTANT: docker-compose mounts vector-store/ to initdb.d. Files here still
-- get executed on FIRST boot (subdirectory?). Postgres entrypoint only runs
-- files in the TOP of /docker-entrypoint-initdb.d, not nested folders.
-- How to run on an existing volume (container up):
--   Get-Content data/vector-store/migrations/migrate_add_golang.sql |
--     docker exec -i opn-postgres psql -U opn_admin -d opn_db
-- Then seed with seed_golang_only.sql.
-- SOLID: SRP — golang table + indexes only. Does not wipe other language tables.
-- ==============================================================================

CREATE TABLE IF NOT EXISTS persons_golang (
    id UUID PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age >= 0),
    sex VARCHAR(20) NOT NULL,
    marital_status VARCHAR(20) NOT NULL,
    children_count INT NOT NULL CHECK (children_count >= 0),
    living_place VARCHAR(50) NOT NULL,
    occupation VARCHAR(50) NOT NULL,
    national_code VARCHAR(10) NOT NULL,
    embedding vector(384),
    has_passport BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_persons_golang_national_code ON persons_golang (national_code);
CREATE INDEX IF NOT EXISTS idx_persons_golang_marital_status ON persons_golang (marital_status);
CREATE INDEX IF NOT EXISTS idx_persons_golang_sex ON persons_golang (sex);
CREATE INDEX IF NOT EXISTS idx_persons_golang_embedding ON persons_golang USING hnsw (embedding vector_l2_ops);
