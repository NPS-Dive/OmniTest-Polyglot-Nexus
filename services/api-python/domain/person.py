"""
File: domain/person.py
Purpose: Language-agnostic Person entity (no SQLAlchemy, no protobuf).
SOLID: SRP — data only. Persistence and gRPC mapping live elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID


@dataclass
class Person:
    """Domain person. Categoricals are the VARCHAR seed labels (e.g. male, job seeker)."""

    first_name: str
    last_name: str
    age: int
    sex: str
    marital_status: str
    children_count: int
    living_place: str
    occupation: str
    national_code: str
    id: Optional[UUID] = None
    has_passport: bool = False
    embedding: Optional[List[float]] = field(default=None)


@dataclass
class PersonFilter:
    """SearchByFilter criteria. None means do not constrain that field."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    sex: Optional[str] = None
    national_code: Optional[str] = None
