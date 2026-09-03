/**
 * @file domain/IPersonRepository.ts
 * @description DIP contract. Controller must not import pg.
 * SOLID: ISP — only the four Person operations the gRPC API needs.
 */

import { Person, PersonFilter } from './Person.js';

/**
 * Paginated / filtered result. totalCount is COUNT(*) of the matching set,
 * not the page length — required for fair six-language comparison.
 */
export interface PersonPage {
    items: Person[];
    totalCount: number;
}

export interface IPersonRepository {
    create(person: Person): Promise<Person>;
    readAll(limit: number, offset: number): Promise<PersonPage>;
    searchByFilter(filters: PersonFilter, limit: number): Promise<PersonPage>;
    searchByVector(vector: number[], topK: number): Promise<Person[]>;
}
