"""
File: infrastructure/db/person_entity.py
Purpose: ORM mapping to persons_python. Not imported by presentation.
SOLID: SRP — table mapping only. Domain Person is a separate dataclass.
"""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PersonEntity(Base):
    """Row shape of persons_python. Column names match 02_create_tables.sql."""

    __tablename__ = "persons_python"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(20), nullable=False)
    marital_status = Column(String(20), nullable=False)
    children_count = Column(Integer, nullable=False)
    living_place = Column(String(50), nullable=False)
    occupation = Column(String(50), nullable=False)
    national_code = Column(String(10), nullable=False)
    embedding = Column(Vector(384))
    has_passport = Column(Boolean, nullable=False, default=False)
