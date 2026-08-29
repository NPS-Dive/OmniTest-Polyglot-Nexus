"""
File: data/mock-generator/embedding_updater.py
Purpose: Backfill pgvector embeddings for persons_* tables that still have NULL
         embedding columns. Skips rows that already have vectors (preserves the
         completed 1M all-MiniLM-L6-v2 run).
SOLID:
  - SRP: DatabaseManager = SQL; EmbeddingService = model; Orchestrator = ETL flow
  - DIP: Orchestrator depends on those types, not on psycopg2/transformers directly
  - OCP: --tables lets us add persons_golang without editing the ETL loop
Dependencies: psycopg2, sentence-transformers, numpy (see requirements.txt)
"""

from __future__ import annotations

import argparse
import os
from typing import Iterator, List, Optional, Sequence, Tuple

import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

# Contract: every language table in opn_db. Do not invent extra names here.
DEFAULT_TABLES = (
    "persons_csharp",
    "persons_python",
    "persons_java",
    "persons_node",
    "persons_cpp",
    "persons_golang",
)


class DatabaseManager:
    """
    Owns the PostgreSQL connection and batch I/O.
    SRP: no model inference lives here.
    """

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self.conn = None

    def connect(self) -> None:
        """Open a single session used for the whole table pass."""
        self.conn = psycopg2.connect(self.connection_string)

    def table_exists(self, table_name: str) -> bool:
        """Guard so --tables persons_golang does not crash before migrate_add_golang.sql."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (table_name,))
            return cur.fetchone()[0] is not None

    def fetch_unembedded_records(
        self, table_name: str, batch_size: int, limit: Optional[int] = None
    ) -> Iterator[list]:
        """
        Yields only rows where embedding IS NULL (skip already-backfilled vectors).
        Identifier interpolation is restricted to DEFAULT_TABLES via the CLI allow-list.
        """
        query_limit = f"LIMIT {int(limit)}" if limit else ""
        query = f"""
            SELECT id, first_name, last_name, age, sex, marital_status, occupation, living_place
            FROM {table_name}
            WHERE embedding IS NULL
            {query_limit}
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            while True:
                records = cur.fetchmany(batch_size)
                if not records:
                    break
                yield records

    def update_embeddings_in_batch(self, table_name: str, data: list) -> None:
        """Bulk UPDATE via VALUES list. embedding column is vector(384)."""
        query = f"""
            UPDATE {table_name} AS t
            SET embedding = e.embedding::vector
            FROM (VALUES %s) AS e(id, embedding)
            WHERE t.id = e.id::uuid;
        """
        with self.conn.cursor() as cur:
            execute_values(cur, query, data)
        self.conn.commit()

    def vacuum_analyze(self, table_name: str) -> None:
        """
        Refresh planner stats after a large UPDATE. Must run outside a transaction
        (AUTOCOMMIT) — required after embedding 1M rows.
        """
        old_isolation = self.conn.isolation_level
        self.conn.set_isolation_level(0)
        with self.conn.cursor() as cur:
            cur.execute(f"VACUUM ANALYZE {table_name};")
        self.conn.set_isolation_level(old_isolation)

    def close(self) -> None:
        """Release the connection even if the pipeline failed mid-batch."""
        if self.conn:
            self.conn.close()
            self.conn = None


class EmbeddingService:
    """
    Wraps sentence-transformers. SRP: text + vectors only.
    Model all-MiniLM-L6-v2 MUST stay 384-dim to match the SQL column.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        print(f"Loading AI Model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully.")

    def create_semantic_text(self, record: tuple) -> str:
        """
        One English sentence per person so the vector encodes identity + categories.
        Seed CSV uses lowercase labels (male, job seeker); strip proto prefixes if present.
        """
        def clean(value: str) -> str:
            text = (value or "").replace("SEX_", "").replace("MARITAL_STATUS_", "")
            text = text.replace("OCCUPATION_", "").replace("LIVING_PLACE_", "")
            return text.replace("_", " ")

        return (
            f"Person named {record[1]} {record[2]}, age {record[3]}. "
            f"Sex: {clean(record[4])}. "
            f"Status: {clean(record[5])}. "
            f"Works as: {clean(record[6])}. "
            f"Lives in: {clean(record[7])}."
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Batch encode. Returns Python lists for psycopg2 vector cast."""
        embeddings = self.model.encode(texts)
        return [embedding.tolist() for embedding in embeddings]


class PipelineOrchestrator:
    """
    Composition root helper: extract NULL embeddings → encode → UPDATE → VACUUM.
    """

    def __init__(self, db: DatabaseManager, ai: EmbeddingService) -> None:
        self.db = db
        self.ai = ai

    def run(self, table_name: str, batch_size: int = 1000, max_records: Optional[int] = None) -> None:
        """Process one table. Safe to re-run: already-embedded rows are skipped."""
        if not self.db.table_exists(table_name):
            print(f"SKIP {table_name}: table does not exist. Run migrations/migrate_add_golang.sql first.")
            return

        print(f"Starting pipeline for table: {table_name}")
        total_processed = 0

        for batch in self.db.fetch_unembedded_records(table_name, batch_size, max_records):
            texts = [self.ai.create_semantic_text(row) for row in batch]
            vectors = self.ai.generate_embeddings(texts)
            update_data = [(row[0], str(vector)) for row, vector in zip(batch, vectors)]
            self.db.update_embeddings_in_batch(table_name, update_data)
            total_processed += len(batch)
            print(f"  {table_name}: processed {total_processed} new embeddings...")

        if total_processed == 0:
            print(f"  {table_name}: nothing to do (all embeddings already present).")
        else:
            print(f"  {table_name}: VACUUM ANALYZE after {total_processed} updates...")
            self.db.vacuum_analyze(table_name)
        print(f"Finished {table_name}.")


def _parse_args() -> argparse.Namespace:
    """CLI: table allow-list, batch size, optional cap for smoke tests."""
    parser = argparse.ArgumentParser(
        description="Backfill pgvector embeddings; skips rows that already have vectors."
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        default=list(DEFAULT_TABLES),
        help="Language tables to process (default: all six).",
    )
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Optional cap per table (smoke). Default: all NULL rows.",
    )
    parser.add_argument(
        "--connection",
        default=os.getenv(
            "OPN_DATABASE_URL",
            "postgresql://opn_admin:opn_secret@localhost:5432/opn_db",
        ),
    )
    return parser.parse_args()


def _assert_allowed_tables(tables: Sequence[str]) -> Tuple[str, ...]:
    """Reject unknown identifiers so we never interpolate user SQL into FROM."""
    allowed = set(DEFAULT_TABLES)
    unknown = [t for t in tables if t not in allowed]
    if unknown:
        raise SystemExit(f"Unknown table(s) {unknown}. Allowed: {sorted(allowed)}")
    return tuple(tables)


if __name__ == "__main__":
    args = _parse_args()
    tables = _assert_allowed_tables(args.tables)

    db_manager = DatabaseManager(args.connection)
    embedding_service = EmbeddingService("all-MiniLM-L6-v2")
    orchestrator = PipelineOrchestrator(db_manager, embedding_service)

    db_manager.connect()
    try:
        for table in tables:
            orchestrator.run(
                table_name=table,
                batch_size=args.batch_size,
                max_records=args.max_records,
            )
    finally:
        db_manager.close()
