import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
import math

# =====================================================================
# SOLID Principles Applied:
# 1. Single Responsibility Principle (SRP): Each class has one job (DB access, Embedding, Orchestration).
# 2. Dependency Inversion Principle (DIP): The orchestrator depends on abstractions (interfaces could be added later for different models/DBs).
# =====================================================================

class DatabaseManager:
    """
    Handles all PostgreSQL database interactions. 
    Keeps connection logic isolated from business logic.
    """
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        """Establishes the database connection."""
        self.conn = psycopg2.connect(self.connection_string)

    def fetch_unembedded_records(self, table_name: str, batch_size: int, limit: int = None) -> list:
        """
        Fetches rows that do not have an embedding yet.
        Uses Yield to return data in chunks, preventing Memory (RAM) overflow.
        """
        query_limit = f"LIMIT {limit}" if limit else ""
        query = f"""
            SELECT id, first_name, last_name, age, sex, marital_status, occupation, living_place 
            FROM {table_name} 
            WHERE embedding IS NULL 
            {query_limit}
        """
        
        with self.conn.cursor() as cur:
            cur.execute(query)
            while True:
                # Fetch only 'batch_size' records at a time
                records = cur.fetchmany(batch_size)
                if not records:
                    break
                yield records

    def update_embeddings_in_batch(self, table_name: str, data: list):
        """
        Updates the database in bulk. 
        Uses execute_values for high performance batch updating.
        """
        query = f"""
            UPDATE {table_name} AS t 
            SET embedding = e.embedding::vector
            FROM (VALUES %s) AS e(id, embedding) 
            WHERE t.id = e.id::uuid;
        """
        with self.conn.cursor() as cur:
            execute_values(cur, query, data)
        self.conn.commit()

    def close(self):
        """Closes the connection safely."""
        if self.conn:
            self.conn.close()


class EmbeddingService:
    """
    Handles the AI/Neural Network generation of vectors.
    Encapsulates the sentence-transformers library.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # This model outputs standard $384$-dimensional vectors
        print(f"Loading AI Model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully.")

    def create_semantic_text(self, record: tuple) -> str:
        """
        Converts a database row into a meaningful English sentence.
        This is what the AI will actually "read" to generate the vector.
        """
        # record mapping based on SQL select order: 
        # 0:id, 1:first_name, 2:last_name, 3:age, 4:sex, 5:marital_status, 6:occupation, 7:living_place
        return (
            f"Person named {record[1]} {record[2]}, age {record[3]}. "
            f"Sex: {record[4].replace('SEX_', '')}. "
            f"Status: {record[5].replace('MARITAL_STATUS_', '')}. "
            f"Works as: {record[6].replace('OCCUPATION_', '')}. "
            f"Lives in: {record[7].replace('LIVING_PLACE_', '')}."
        )

    def generate_embeddings(self, texts: list) -> list:
        """
        Passes a batch of strings to the neural network.
        Returns a list of vectors (lists of floats).
        """
        # encode() returns a numpy array, we convert it to a standard Python list
        embeddings = self.model.encode(texts)
        return [embedding.tolist() for embedding in embeddings]


class PipelineOrchestrator:
    """
    Wires the DatabaseManager and EmbeddingService together.
    Controls the flow of data.
    """
    def __init__(self, db: DatabaseManager, ai: EmbeddingService):
        self.db = db
        self.ai = ai

    def run(self, table_name: str, batch_size: int = 1000, max_records: int = None):
        """
        Executes the ETL (Extract, Transform, Load) process.
        """
        try:
            self.db.connect()
            print(f"Starting pipeline for table: {table_name}")
            
            total_processed = 0
            
            # 1. Extract (Fetch in batches)
            for batch in self.db.fetch_unembedded_records(table_name, batch_size, max_records):
                
                # 2. Transform (Generate text strings, then create Vectors)
                texts = [self.ai.create_semantic_text(row) for row in batch]
                vectors = self.ai.generate_embeddings(texts)
                
                # Prepare data tuple for execute_values: (id, vector_string)
                update_data = [(row[0], str(vector)) for row, vector in zip(batch, vectors)]
                
                # 3. Load (Update DB)
                self.db.update_embeddings_in_batch(table_name, update_data)
                
                total_processed += len(batch)
                print(f"Processed and updated {total_processed} records...")

            print("Pipeline completed successfully.")

        except Exception as e:
            print(f"An error occurred in the pipeline: {e}")
        finally:
            self.db.close()

# =====================================================================
# Main Execution Block
# =====================================================================
if __name__ == "__main__":
    # PostgreSQL connection string for OmniTest-Polyglot-Nexus local Docker
    CONNECTION_STRING = "postgresql://opn_admin:opn_secret@localhost:5432/opn_db"
    
    # Initialize dependencies (Dependency Injection approach)
    db_manager = DatabaseManager(CONNECTION_STRING)
    embedding_service = EmbeddingService('all-MiniLM-L6-v2')
    
    orchestrator = PipelineOrchestrator(db_manager, embedding_service)
    
    # QA/QC STRATEGY: 
    # Set max_records=10000 to generate REAL embeddings for AI RAG testing.
    # Set max_records=None if you truly want to wait for all 1,000,000 records to process.
    orchestrator.run(table_name="persons_csharp", batch_size=1000, max_records=1000000)
