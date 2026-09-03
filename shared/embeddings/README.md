# shared/embeddings

This folder is intentionally empty of binaries.

Embeddings for OmniTest live in Postgres `persons_*.embedding` (`vector(384)`, MiniLM-L6-v2). They are produced by [data/mock-generator/embedding_updater.py](../../data/mock-generator/embedding_updater.py), which skips rows that already have a vector and VACUUM ANALYZE after large updates.

Do not add a second embedding pipeline here. Point RAG / `SearchByVector` at the language-owned table.
