// ============================================================================
// File: src/infrastructure/db/PostgresPersonRepository.ts
// Purpose: Concrete implementation of IPersonRepository for PostgreSQL.
// SOLID Principle: 
// - Liskov Substitution Principle (LSP): This can be swapped with a MongoRepository in the future without breaking the application.
// - Single Responsibility Principle (SRP): Handles only database interactions.
// ============================================================================

import pg from 'pg';
import { IPersonRepository, Person } from '../../domain/IPersonRepository.js'; // Note the .js extension for ESM

export class PostgresPersonRepository implements IPersonRepository {
    private pool: pg.Pool;

    /**
     * Dependency Injection of the database pool.
     * Follows Dependency Inversion Principle (DIP) by accepting an abstraction/configured instance.
     * @param pool pg.Pool instance configured in index.ts
     */
    constructor(pool: pg.Pool) {
        this.pool = pool;
    }

    async createPerson(person: Person): Promise<string> {
        // Implementation omitted for brevity, will be implemented in next phases
        throw new Error("Method not implemented.");
    }

    /**
     * Retrieves a paginated list of persons specifically from the Node.js table.
     * Maps 'first_name' to 'name' and 'last_name' to 'family' to match the Domain model.
     * @param limit Number of records to return
     * @param offset Number of records to skip
     */
    async readAllPersons(limit: number, offset: number): Promise<{ persons: Person[], totalCount: number }> {
        const client = await this.pool.connect();
        try {
            // Target the 'persons_node' table and alias columns to match the Domain/Protobuf expectation
            const dataQuery = `
                SELECT 
                    id, 
                    first_name AS name, 
                    last_name AS family, 
                    age, 
                    sex, 
                    marital_status, 
                    children_count, 
                    living_place, 
                    occupation, 
                    national_code 
                FROM persons_node 
                LIMIT $1 OFFSET $2;
            `;
            
            // Fast estimation for total count on the Node table
            const countQuery = `SELECT reltuples::bigint AS estimate FROM pg_class WHERE relname = 'persons_node';`;

            const [dataResult, countResult] = await Promise.all([
                client.query(dataQuery, [limit, offset]),
                client.query(countQuery)
            ]);

            return {
                persons: dataResult.rows,
                totalCount: parseInt(countResult.rows[0].estimate, 10)
            };
        } finally {
            client.release();
        }
    }

    /**
     * Performs a semantic search using pgvector on the Node.js table.
     * @param vector The query embedding vector
     * @param topK Number of closest results to return
     */
    async searchByVector(vector: number[], topK: number): Promise<{ persons: Person[], totalCount: number }> {
        const client = await this.pool.connect();
        try {
            // Format array for pgvector string requirement: '[0.1, 0.2, ...]'
            const vectorString = `[${vector.join(',')}]`;
            
            // Target 'persons_node' and alias columns.
            // Using cosine distance operator (<=>) for vector comparison.
            const query = `
                SELECT 
                    id, 
                    first_name AS name, 
                    last_name AS family, 
                    age, 
                    sex, 
                    marital_status, 
                    children_count, 
                    living_place, 
                    occupation, 
                    national_code 
                FROM persons_node 
                ORDER BY embedding <=> $1 
                LIMIT $2;
            `;
            
            const result = await client.query(query, [vectorString, topK]);

            return {
                persons: result.rows,
                totalCount: result.rows.length
            };
        } finally {
            client.release();
        }
    }
}
