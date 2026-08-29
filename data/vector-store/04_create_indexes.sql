-- ==============================================================================
-- File: 04_create_indexes.sql
-- Purpose: B-tree + HNSW indexes AFTER bulk COPY (avoids index maintenance
-- during 1M-row ingest). Lexical name 04_ so Docker init runs after 03_seed.
-- SOLID: SRP — indexes only. Vector metric is L2 (vector_l2_ops) to match
-- SearchByVector using the <-> operator in every language API.
-- ==============================================================================

CREATE OR REPLACE FUNCTION create_table_indexes(table_name text) RETURNS void AS $$
BEGIN
    -- Exact match: national_code filter and uniqueness-style lookups
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_national_code ON %I (national_code);', table_name, table_name);

    -- Categorical filter used by SearchByFilter
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_marital_status ON %I (marital_status);', table_name, table_name);
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_sex ON %I (sex);', table_name, table_name);

    -- ANN for RAG / SearchByVector — L2, not cosine, by contract
    EXECUTE format(
        'CREATE INDEX IF NOT EXISTS idx_%I_embedding ON %I USING hnsw (embedding vector_l2_ops);',
        table_name, table_name
    );
END;
$$ LANGUAGE plpgsql;

SELECT create_table_indexes('persons_csharp');
SELECT create_table_indexes('persons_cpp');
SELECT create_table_indexes('persons_java');
SELECT create_table_indexes('persons_node');
SELECT create_table_indexes('persons_python');
SELECT create_table_indexes('persons_golang');

DROP FUNCTION create_table_indexes(text);
