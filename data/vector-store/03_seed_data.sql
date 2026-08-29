-- ==============================================================================
-- File: 03_seed_data.sql
-- Purpose: Load the same master_seed.csv into every language table.
-- Why COPY (server-side), not \copy: docker-entrypoint-initdb.d executes .sql
-- via psql, but the CSV is mounted at /master_seed.csv inside the container
-- (see shared/infrastructure/docker-compose.yml). Server COPY reads that path.
-- SOLID: SRP — ingestion only. Indexes are created AFTER this file (04_).
-- Note: this script runs only on a FRESH volume. Existing DBs use
-- migrate_add_golang.sql and/or seed_golang_only.sql instead.
-- ==============================================================================

-- Same column list as data/master_seed.csv header.
-- has_passport and embedding stay at defaults (false / NULL) during seed.

COPY persons_csharp (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);

COPY persons_cpp (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);

COPY persons_java (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);

COPY persons_node (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);

COPY persons_python (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);

COPY persons_golang (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code)
FROM '/master_seed.csv' WITH (FORMAT csv, HEADER true);
