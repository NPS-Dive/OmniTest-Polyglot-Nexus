"""
File: domain/i_person_repository.py
Purpose: Persistence contract. Presentation depends on this ABC, not SQLAlchemy.
SOLID: DIP + ISP — only the Person operations the gRPC API needs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from domain.person import Person, PersonFilter


class IPersonRepository(ABC):
    """Abstract data access for persons_python."""

    @abstractmethod
    def create(self, person: Person) -> Person:
        """Insert and return the row including generated id."""

    @abstractmethod
    def read_all(self, limit: int, offset: int) -> Tuple[List[Person], int]:
        """Paginated list plus count of rows in this page."""

    @abstractmethod
    def search_by_filter(self, filters: PersonFilter, limit: int) -> List[Person]:
        """AND-combine provided filters."""

    @abstractmethod
    def search_by_vector(self, vector: List[float], top_k: int) -> List[Person]:
        """Nearest neighbors by L2 (<->) on embedding."""
