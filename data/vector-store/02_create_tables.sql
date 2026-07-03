-- ==============================================================================
-- File: 02_create_tables.sql
-- Responsibility: Define the schema for the Polyglot API backend.
-- Rationale: We create 5 identical, independent tables. 
-- Why? To prevent Database Contention (Row/Table locks) during our k6 load tests. 
-- If all 5 languages hit the same table with $10,000$ Concurrent VUs, the DB 
-- becomes the bottleneck, masking the actual API performance differences.
-- ==============================================================================

-- Define a reusable PL/pgSQL function to create our tables dynamically.
-- This adheres to the DRY (Don't Repeat Yourself) principle in SQL.
CREATE OR REPLACE FUNCTION create_person_table(table_name text) RETURNS void AS $$
BEGIN
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I (
            -- Primary Key: UUID matching our Python generator
            id UUID PRIMARY KEY,
            
            -- Basic Identity Data
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            age INT NOT NULL CHECK (age >= 0),
            
            -- Categorical Data
            sex VARCHAR(20) NOT NULL,
            marital_status VARCHAR(20) NOT NULL,
            children_count INT NOT NULL CHECK (children_count >= 0),
            living_place VARCHAR(50) NOT NULL,
            occupation VARCHAR(50) NOT NULL,
            
            -- Business Data
            national_code VARCHAR(10) NOT NULL,
            
            -- AI/RAG Data: Storing embeddings for semantic search.
            -- Using 384 dimensions (Standard for lightweight local models like all-MiniLM-L6-v2).
            -- This can be updated to 1536 if we switch to OpenAI embeddings.
            embedding vector(384) 
        );
    ', table_name);
END;
$$ LANGUAGE plpgsql;

-- Execute the function to create a dedicated table for each language
SELECT create_person_table('persons_csharp');
SELECT create_person_table('persons_cpp');
SELECT create_person_table('persons_java');
SELECT create_person_table('persons_node');
SELECT create_person_table('persons_python');

-- Clean up the function as it is no longer needed (Memory Management)
DROP FUNCTION create_person_table(text);
