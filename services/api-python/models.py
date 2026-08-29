"""
Domain Models Layer.
This module defines the SQLAlchemy ORM models, representing our core business entities.
It strictly adheres to the Single Responsibility Principle (SRP) by only managing data structure mapping.
"""
import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

# Base class for declarative SQLAlchemy models
Base = declarative_base()

class PersonEntity(Base):
    """
    Represents a person record mapped to the 'persons_python' table in PostgreSQL.
    """
    __tablename__ = 'persons_python'

    # Mapped to Postgres UUID, auto-generates on insert if omitted
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Map the Python attribute 'name' to the DB column 'first_name'
    name = Column('first_name', String(100), nullable=False)
    
    # Map the Python attribute 'family' to the DB column 'last_name'
    family = Column('last_name', String(100), nullable=False)
    
    age = Column(Integer, nullable=False)
    
    # DB expects VARCHAR for these Enum fields
    sex = Column(String(20), nullable=False)
    marital_status = Column(String(20), nullable=False)
    children_count = Column(Integer, nullable=False)
    living_place = Column(String(50), nullable=False)
    occupation = Column(String(50), nullable=False)
    
    # Updated to String(10) to match Postgres exact schema
    national_code = Column(String(10), unique=True, index=True, nullable=False)
    
    # Vector column storing 384-dimensional embeddings (for RAG/Semantic Search)
    embedding = Column(Vector(384))
