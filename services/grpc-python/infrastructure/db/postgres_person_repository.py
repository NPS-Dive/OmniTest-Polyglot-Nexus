"""
File: infrastructure/db/postgres_person_repository.py
Purpose: IPersonRepository against persons_python using L2 distance.
SOLID: LSP — drop-in for the domain interface.
"""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import asc, func
from sqlalchemy.orm import Session

from domain.i_person_repository import IPersonRepository
from domain.person import Person, PersonFilter
from infrastructure.db.person_entity import PersonEntity


def _to_domain(entity: PersonEntity) -> Person:
    """ORM row to domain. embedding may be None for un-backfilled seed rows."""
    vec = list(entity.embedding) if entity.embedding is not None else None
    return Person(
        id=entity.id,
        first_name=entity.first_name,
        last_name=entity.last_name,
        age=entity.age,
        sex=entity.sex,
        marital_status=entity.marital_status,
        children_count=entity.children_count,
        living_place=entity.living_place,
        occupation=entity.occupation,
        national_code=entity.national_code,
        has_passport=bool(entity.has_passport),
        embedding=vec,
    )


class PostgresPersonRepository(IPersonRepository):
    """Concrete Postgres adapter. Session is injected (DIP)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, person: Person) -> Person:
        entity = PersonEntity(
            first_name=person.first_name,
            last_name=person.last_name,
            age=person.age,
            sex=person.sex,
            marital_status=person.marital_status,
            children_count=person.children_count,
            living_place=person.living_place,
            occupation=person.occupation,
            national_code=person.national_code,
            embedding=person.embedding,
            has_passport=person.has_passport,
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return _to_domain(entity)

    def read_all(self, limit: int, offset: int) -> Tuple[List[Person], int]:
        # COUNT(*) keeps Python total_count comparable with Go/Java/C++.
        total = int(self.db.query(func.count(PersonEntity.id)).scalar() or 0)
        rows = (
            self.db.query(PersonEntity)
            .order_by(asc(PersonEntity.id))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [_to_domain(r) for r in rows], total

    def search_by_filter(self, filters: PersonFilter, limit: int) -> Tuple[List[Person], int]:
        query = self.db.query(PersonEntity)
        if filters.first_name:
            query = query.filter(PersonEntity.first_name.ilike(f"%{filters.first_name}%"))
        if filters.last_name:
            query = query.filter(PersonEntity.last_name.ilike(f"%{filters.last_name}%"))
        if filters.min_age is not None:
            query = query.filter(PersonEntity.age >= filters.min_age)
        if filters.max_age is not None:
            query = query.filter(PersonEntity.age <= filters.max_age)
        if filters.sex:
            # Case-insensitive: seed "male" and leftover "MALE" both match.
            query = query.filter(func.lower(PersonEntity.sex) == filters.sex.lower())
        if filters.national_code:
            query = query.filter(PersonEntity.national_code == filters.national_code)
        total = int(query.with_entities(func.count(PersonEntity.id)).scalar() or 0)
        rows = query.order_by(asc(PersonEntity.id)).limit(limit).all()
        return [_to_domain(r) for r in rows], total

    def search_by_vector(self, vector: List[float], top_k: int) -> List[Person]:
        rows = (
            self.db.query(PersonEntity)
            .filter(PersonEntity.embedding.isnot(None))
            .order_by(PersonEntity.embedding.l2_distance(vector))
            .limit(top_k)
            .all()
        )
        return [_to_domain(r) for r in rows]
