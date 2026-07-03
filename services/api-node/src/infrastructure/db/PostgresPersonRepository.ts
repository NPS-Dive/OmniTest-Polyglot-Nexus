import { Pool } from 'pg';
import { IPersonRepository, PersonFilter } from '../../domain/IPersonRepository.js';

/**
 * PostgreSQL implementation of the Person Repository.
 * Handles all direct database interactions using node-postgres (pg).
 */
export class PostgresPersonRepository implements IPersonRepository {
    private pool: Pool;

    constructor(pool: Pool) {
        this.pool = pool;
    }

    public async create(person: any): Promise<any> {
        const query = `
            INSERT INTO persons_node (
                id, first_name, last_name, age, sex, marital_status, 
                children_count, living_place, occupation, national_code, embedding
            ) VALUES (
                gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
            ) RETURNING id;
        `;
        const values = [
            person.first_name, person.last_name, person.age, person.sex, 
            person.marital_status, person.children_count, person.living_place, 
            person.occupation, person.national_code, person.embedding
        ];
        
        try {
            const result = await this.pool.query(query, values);
            return result.rows[0];
        } catch (error: any) {
            console.error('[DB] Error creating person:', error.message);
            throw error;
        }
    }

    public async readAll(limit = 10, offset = 0): Promise<any[]> {
        const query = `
            SELECT id, first_name AS name, last_name AS family, age, sex, 
                   marital_status AS "maritalStatus", children_count AS "childrenCount", 
                   living_place AS "livingPlace", occupation, national_code AS "nationalCode" 
            FROM persons_node 
            LIMIT $1 OFFSET $2;
        `;
        const result = await this.pool.query(query, [limit, offset]);
        return result.rows;
    }

    public async searchByVector(vector: number[], limit = 5): Promise<any[]> {
        // Convert vector array to pgvector string format: '[1,2,3]'
        const vectorString = `[${vector.join(',')}]`;
        const query = `
            SELECT id, first_name AS name, last_name AS family, national_code, 
                   embedding <-> $1 AS distance 
            FROM persons_node 
            ORDER BY distance 
            LIMIT $2;
        `;
        const result = await this.pool.query(query, [vectorString, limit]);
        return result.rows;
    }

    /**
     * Searches persons by partial name/family and exact national code.
     * Uses ILIKE for case-insensitive partial matching on names.
     */
    public async searchByFilter(filters: any): Promise<any[]> {
        // Start with a base query
        let query = `
            SELECT id, first_name AS name, last_name AS family, age, sex, 
                   marital_status AS "maritalStatus", children_count AS "childrenCount", 
                   living_place AS "livingPlace", occupation, national_code AS "nationalCode" 
            FROM persons_node 
            WHERE 1=1
        `;
        
        const values: any[] = [];
        let paramIndex = 1;

        // Dynamically append filters if they are valid, non-empty strings
        if (typeof filters.firstName === 'string' && filters.firstName.trim() !== "") {
            query += ` AND first_name ILIKE $${paramIndex}`;
            values.push(`%${filters.firstName.trim()}%`);
            paramIndex++;
        }
        
        if (typeof filters.lastName === 'string' && filters.lastName.trim() !== "") {
            query += ` AND last_name ILIKE $${paramIndex}`;
            values.push(`%${filters.lastName.trim()}%`);
            paramIndex++;
        }
        
        if (typeof filters.nationalCode === 'string' && filters.nationalCode.trim() !== "") {
            query += ` AND national_code = $${paramIndex}`;
            values.push(filters.nationalCode.trim());
            paramIndex++;
        }

        // Add a hard limit to prevent dumping the entire database if no filters are provided
        query += ` LIMIT 100`;

        // Log the final query and values to help debugging
        console.log("[DB] Executing Query:", query.trim().replace(/\s+/g, ' '));
        console.log("[DB] With Values:", values);

        const result = await this.pool.query(query, values);
        return result.rows;
    }
}
