-- ==============================================================================
-- File: 01_init_extensions.sql
-- Purpose: Enable PostgreSQL extensions required by every language table.
-- SOLID: SRP — extensions only. Schema, seed, and indexes live in later scripts.
-- Runs first under docker-entrypoint-initdb.d (lexical order 01_).
-- ==============================================================================

-- pgvector: stores 384-dim embeddings (all-MiniLM-L6-v2) and provides
-- L2 distance operator <-> used by SearchByVector in all six gRPC APIs.
CREATE EXTENSION IF NOT EXISTS vector;
