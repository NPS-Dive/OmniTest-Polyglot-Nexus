// services/api-node/src/domain/IPersonRepository.ts

/**
 * Defines the allowed filters for searching persons.
 * Follows the Open/Closed Principle (OCP) by using optional properties.
 */
export interface PersonFilter {
    firstName?: string;
    lastName?: string;
    nationalCode?: string;
}

/**
 * Interface representing the data access contract for Person entities.
 * Follows the Dependency Inversion Principle (DIP).
 */
export interface IPersonRepository {
    /**
     * Creates a new person record.
     */
    create(person: any): Promise<any>;

    /**
     * Retrieves a paginated list of persons.
     */
    readAll(limit?: number, offset?: number): Promise<any[]>;

    /**
     * Searches for persons based on a vector embedding using pgvector.
     */
    searchByVector(vector: number[], limit: number): Promise<any[]>;
    
    /**
     * Searches for persons based on specific text/value filters.
     * @param filters - The filtering criteria (firstName, lastName, nationalCode)
     */
    searchByFilter(filters: PersonFilter): Promise<any[]>;
}
