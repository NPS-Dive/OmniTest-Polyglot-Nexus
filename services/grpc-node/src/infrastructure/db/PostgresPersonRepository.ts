/**
 * @file infrastructure/db/PostgresPersonRepository.ts
 * @description persons_node only. Vector search uses L2 <-> .
 * SOLID: LSP implementation of IPersonRepository.
 */

import { Pool, QueryResultRow } from 'pg';
import { IPersonRepository, PersonPage } from '../../domain/IPersonRepository.js';
import { Person, PersonFilter } from '../../domain/Person.js';

/** SQL twin of Go's normalizeLabel — matches "male", "MALE", "SEX_MALE". */
const NORM_SEX = `trim(both from regexp_replace(
    regexp_replace(replace(replace(lower(sex), '_', ' '), '-', ' '), '\\s+', ' ', 'g'),
    '^(sex) ',
    ''
))`;

const SELECT_COLS = `
    id, first_name, last_name, age, sex, marital_status, children_count,
    living_place, occupation, national_code, has_passport, embedding
`;

function mapRow(row: QueryResultRow): Person {
    let embedding: number[] | undefined;
    if (row.embedding) {
        const raw = String(row.embedding).replace(/[\[\]]/g, '');
        embedding = raw ? raw.split(',').map(Number) : undefined;
    }
    return {
        id: String(row.id),
        firstName: row.first_name,
        lastName: row.last_name,
        age: Number(row.age),
        sex: row.sex,
        maritalStatus: row.marital_status,
        childrenCount: Number(row.children_count),
        livingPlace: row.living_place,
        occupation: row.occupation,
        nationalCode: row.national_code,
        hasPassport: Boolean(row.has_passport),
        embedding
    };
}

export class PostgresPersonRepository implements IPersonRepository {
    constructor(private readonly pool: Pool) {}

    public async create(person: Person): Promise<Person> {
        const vector = person.embedding ? `[${person.embedding.join(',')}]` : null;
        const result = await this.pool.query(
            `INSERT INTO persons_node (
                id, first_name, last_name, age, sex, marital_status, children_count,
                living_place, occupation, national_code, embedding, has_passport
            ) VALUES (gen_random_uuid(), $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            RETURNING ${SELECT_COLS}`,
            [
                person.firstName, person.lastName, person.age, person.sex,
                person.maritalStatus, person.childrenCount, person.livingPlace,
                person.occupation, person.nationalCode, vector, person.hasPassport
            ]
        );
        return mapRow(result.rows[0]);
    }

    public async readAll(limit: number, offset: number): Promise<PersonPage> {
        const count = await this.pool.query('SELECT COUNT(*)::int AS n FROM persons_node');
        const result = await this.pool.query(
            `SELECT ${SELECT_COLS} FROM persons_node ORDER BY id LIMIT $1 OFFSET $2`,
            [limit, offset]
        );
        return { items: result.rows.map(mapRow), totalCount: Number(count.rows[0].n) };
    }

    public async searchByFilter(filters: PersonFilter, limit: number): Promise<PersonPage> {
        const clauses: string[] = ['1=1'];
        const values: unknown[] = [];
        let i = 1;
        if (filters.firstName) {
            clauses.push(`first_name ILIKE $${i++}`);
            values.push(`%${filters.firstName}%`);
        }
        if (filters.lastName) {
            clauses.push(`last_name ILIKE $${i++}`);
            values.push(`%${filters.lastName}%`);
        }
        if (filters.minAge !== undefined) {
            clauses.push(`age >= $${i++}`);
            values.push(filters.minAge);
        }
        if (filters.maxAge !== undefined) {
            clauses.push(`age <= $${i++}`);
            values.push(filters.maxAge);
        }
        if (filters.sex) {
            // Normalized compare so leftover UPPERCASE C++-style rows still match seed labels.
            clauses.push(`${NORM_SEX} = $${i++}`);
            values.push(filters.sex.replace(/[_-]+/g, ' ').trim().toLowerCase().replace(/^sex\s+/, ''));
        }
        if (filters.nationalCode) {
            clauses.push(`national_code = $${i++}`);
            values.push(filters.nationalCode);
        }
        const where = clauses.join(' AND ');
        const count = await this.pool.query(
            `SELECT COUNT(*)::int AS n FROM persons_node WHERE ${where}`,
            values
        );
        values.push(limit);
        const result = await this.pool.query(
            `SELECT ${SELECT_COLS} FROM persons_node WHERE ${where} ORDER BY id LIMIT $${i}`,
            values
        );
        return { items: result.rows.map(mapRow), totalCount: Number(count.rows[0].n) };
    }

    public async searchByVector(vector: number[], topK: number): Promise<Person[]> {
        const literal = `[${vector.join(',')}]`;
        const result = await this.pool.query(
            `SELECT ${SELECT_COLS} FROM persons_node
             WHERE embedding IS NOT NULL
             ORDER BY embedding <-> $1
             LIMIT $2`,
            [literal, topK]
        );
        return result.rows.map(mapRow);
    }
}
