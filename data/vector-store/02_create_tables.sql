-- ==============================================================================
-- File: 02_create_tables.sql
-- Purpose: Create one isolated persons_* table per language in a SINGLE database
--          (opn_db). This is table-per-language isolation, not database-per-language.
-- Why separate tables: k6 concurrent VUs must not contend on the same heap/indexes,
-- so measured latency reflects the API, not shared row locks.
-- SOLID: DRY via create_person_table(); SRP — schema only, no seed/index.
-- Canonical contract (do not rename columns to match proto field names):
--   proto.gender          -> column sex
--   proto.job_category    -> column occupation
--   proto.embedding_vector-> column embedding
--   proto.has_passport    -> column has_passport
--   proto.birth_date      -> NOT stored; APIs derive ISO date from age on read
-- ==============================================================================

-- Reusable factory so all six tables stay byte-identical in structure (OCP:
-- add a language by calling the function, not by copy-pasting CREATE TABLE).
CREATE OR REPLACE FUNCTION create_person_table(table_name text) RETURNS void AS $$
BEGIN
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I (
            -- Matches mock-generator UUID primary key
            id UUID PRIMARY KEY,

            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            age INT NOT NULL CHECK (age >= 0),

            -- VARCHAR categoricals: store proto enum names WITHOUT prefix
            -- e.g. MALE not SEX_MALE. APIs map to/from proto enums.
            sex VARCHAR(20) NOT NULL,
            marital_status VARCHAR(20) NOT NULL,
            children_count INT NOT NULL CHECK (children_count >= 0),
            living_place VARCHAR(50) NOT NULL,
            occupation VARCHAR(50) NOT NULL,

            national_code VARCHAR(10) NOT NULL,

            -- 384 dims = sentence-transformers all-MiniLM-L6-v2
            embedding vector(384),

            -- Proto has_passport; existing 1M seed rows default false
            has_passport BOOLEAN NOT NULL DEFAULT FALSE
        );
    ', table_name);
END;
$$ LANGUAGE plpgsql;

-- One table per gRPC implementation. Rows are identical across tables after seed.
SELECT create_person_table('persons_csharp');
SELECT create_person_table('persons_cpp');
SELECT create_person_table('persons_java');
SELECT create_person_table('persons_node');
SELECT create_person_table('persons_python');
SELECT create_person_table('persons_golang');

DROP FUNCTION create_person_table(text);
