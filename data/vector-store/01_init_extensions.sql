-- ==============================================================================
-- File: 01_init_extensions.sql
-- Responsibility: Initialize required PostgreSQL extensions.
-- Rationale: We separate extensions from schema creation to prevent 
-- permission conflicts (extensions often require superuser rights).
-- ==============================================================================

-- Enable pgvector for AI/RAG integration.
-- This allows us to store high-dimensional embeddings for semantic search
-- via the 'POST /search' endpoint across our Polyglot APIs.
CREATE EXTENSION IF NOT EXISTS vector;

