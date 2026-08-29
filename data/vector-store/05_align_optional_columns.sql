-- ==============================================================================
-- File: 05_align_optional_columns.sql
-- Purpose: Add proto-aligned optional columns to EXISTING tables without
-- rewriting 1M rows. Safe to re-run (IF NOT EXISTS).
-- Fresh installs already get has_passport from 02_create_tables.sql; this
-- script is for volumes created before that column existed.
-- SOLID: SRP — additive schema alignment only. Does not seed or re-embed.
-- ==============================================================================

DO $$
DECLARE
    t text;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'persons_csharp',
        'persons_cpp',
        'persons_java',
        'persons_node',
        'persons_python',
        'persons_golang'
    ]
    LOOP
        -- Skip tables that do not exist yet (golang may be added by migrate_add_golang.sql)
        IF to_regclass(t) IS NULL THEN
            RAISE NOTICE 'Skipping missing table %', t;
            CONTINUE;
        END IF;

        EXECUTE format(
            'ALTER TABLE %I ADD COLUMN IF NOT EXISTS has_passport BOOLEAN NOT NULL DEFAULT FALSE',
            t
        );
    END LOOP;
END $$;
