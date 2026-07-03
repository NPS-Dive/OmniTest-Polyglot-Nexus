-- ==============================================================================
-- File: 03_seed_data.sql
-- Responsibility: Ingest the master_seed.csv into all 5 tables.
-- Rationale: Using the native PostgreSQL \copy command for maximum throughput.
-- This bypasses standard SQL INSERT overhead, crucial for $1,000,000$ records.
-- Note: \copy is a psql client command. 
-- ==============================================================================

-- Turn on timing to benchmark the ingestion process (QA/QC best practice)
\timing on

-- Ingest data into the C# table
-- CSV HEADER tells Postgres to skip the first row (column names)
\copy persons_csharp (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code) FROM '../master_seed.csv' WITH (FORMAT csv, HEADER true);

-- Ingest data into the C++ table
\copy persons_cpp (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code) FROM '../master_seed.csv' WITH (FORMAT csv, HEADER true);

-- Ingest data into the Java table
\copy persons_java (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code) FROM '../master_seed.csv' WITH (FORMAT csv, HEADER true);

-- Ingest data into the Node.js table
\copy persons_node (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code) FROM '../master_seed.csv' WITH (FORMAT csv, HEADER true);

-- Ingest data into the Python table
\copy persons_python (id, first_name, last_name, age, sex, marital_status, children_count, living_place, occupation, national_code) FROM '../master_seed.csv' WITH (FORMAT csv, HEADER true);

\timing off
