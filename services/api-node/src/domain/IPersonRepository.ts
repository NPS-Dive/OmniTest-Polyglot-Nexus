// ============================================================================
// File: src/domain/IPersonRepository.ts
// Purpose: Defines the abstract contract for data persistence operations.
// SOLID Principle: Dependency Inversion Principle (DIP). High-level modules 
// (Controllers) depend on this abstraction, not concrete DB implementations.
// ============================================================================

export interface Person {
    id: string;
    name: string;
    family: string;
    age: number;
    sex: number;
    marital_status: number;
    children_count: number;
    living_place: number;
    occupation: number;
    national_code: string;
}

export interface IPersonRepository {
    /**
     * Inserts a new person into the database.
     * @param person The person domain entity.
     * @returns A promise resolving to the inserted UUID.
     */
    createPerson(person: Person): Promise<string>;

    /**
     * Retrieves a paginated list of persons.
     * @param limit Maximum number of records.
     * @param offset Number of records to skip.
     * @returns A promise containing the persons array and total count.
     */
    readAllPersons(limit: number, offset: number): Promise<{ persons: Person[], totalCount: number }>;

    /**
     * Performs a semantic search using vector similarity (pgvector HNSW index).
     * @param vector The 384-dimensional embedding vector.
     * @param topK The number of nearest neighbors to retrieve.
     */
    searchByVector(vector: number[], topK: number): Promise<{ persons: Person[], totalCount: number }>;

    // Note: searchByFilter can be added here following the same pattern
}
