"""
Infrastructure Layer: Repository Pattern.
Abstracts all raw SQL/ORM queries, adhering to the Dependency Inversion Principle (DIP).
The upper service layers depend on this class, not the database directly.
"""
from sqlalchemy.orm import Session
from sqlalchemy import asc
from models import PersonEntity

class PersonRepository:
    """
    Encapsulates all database operations for the Person entity.
    """
    def __init__(self, db_session: Session):
        # Inject the database session (Dependency Injection)
        self.db = db_session

    def get_all(self, limit: int, offset: int) -> list[PersonEntity]:
        """
        Retrieves a paginated list of persons ordered by ID.
        """
        return self.db.query(PersonEntity).order_by(asc(PersonEntity.id)).offset(offset).limit(limit).all()

    def create(self, person: PersonEntity) -> PersonEntity:
        """
        Persists a new PersonEntity to the database.
        """
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def search_by_filter(self, filters: dict, limit: int = 100) -> list[PersonEntity]:
        """
        Dynamically applies exact-match filters to the query.
        """
        query = self.db.query(PersonEntity)
        
        # Apply filters if they have valid values
        if filters.get("age"):
            query = query.filter(PersonEntity.age == filters["age"])
        if filters.get("occupation"):
            query = query.filter(PersonEntity.occupation == filters["occupation"])
        if filters.get("living_place"):
            query = query.filter(PersonEntity.living_place == filters["living_place"])
            
        return query.limit(limit).all()

    def search_by_vector(self, query_embedding: list[float], limit: int = 5) -> list[PersonEntity]:
        """
        Performs semantic search using pgvector's cosine distance operator (<=>).
        Requires the embedding array to have exactly D = 384 dimensions.
        """
        # Order by Cosine Distance to find the nearest neighbors
        return self.db.query(PersonEntity).order_by(
            PersonEntity.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()
