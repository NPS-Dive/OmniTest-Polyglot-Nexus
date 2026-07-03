-- ==============================================================================
-- File: 04_create_indexes.sql
-- Responsibility: Optimize read and search performance.
-- Rationale: Indexing is performed AFTER bulk insertion (seeding) to avoid 
-- index fragmentation and massive performance penalties during the COPY process.
-- ==============================================================================

CREATE OR REPLACE FUNCTION create_table_indexes(table_name text) RETURNS void AS $$
BEGIN
    -- 1. B-Tree Index for standard exact-match queries (e.g., National Code)
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_national_code ON %I (national_code);', table_name, table_name);
    
    -- 2. B-Tree Index for categorical filtering (used in complex POST /search)
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_marital_status ON %I (marital_status);', table_name, table_name);
    
    -- 3. HNSW (Hierarchical Navigable Small World) Index for pgvector
    -- This provides ultra-fast Approximate Nearest Neighbor (ANN) search for RAG.
    -- We use vector_l2_ops for Euclidean distance, which works well for standard RAG.
    EXECUTE format('CREATE INDEX IF NOT EXISTS idx_%I_embedding ON %I USING hnsw (embedding vector_l2_ops);', table_name, table_name);
END;
$$ LANGUAGE plpgsql;

-- Apply indexes to all tables
SELECT create_table_indexes('persons_csharp');
SELECT create_table_indexes('persons_cpp');
SELECT create_table_indexes('persons_java');
SELECT create_table_indexes('persons_node');
SELECT create_table_indexes('persons_python');

-- Clean up
DROP FUNCTION create_table_indexes(text);
