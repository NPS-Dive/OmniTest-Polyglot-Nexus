"""
Infrastructure Layer: Database Connection Management.
Responsible for creating and maintaining the database engine and session pool.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Define PostgreSQL connection details (matches docker-compose)
DB_USER = os.getenv("POSTGRES_USER", "opn_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "opn_secret")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "opn_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. Create the Engine (connection pool)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 3. Create a configured Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
