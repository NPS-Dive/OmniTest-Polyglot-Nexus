/**
 * @file domain/IPersonRepository.ts
 * @description DIP contract. Controller must not import pg.
 */

import { Person, PersonFilter } from './Person.js';

export interface IPersonRepository {
    create(person: Person): Promise<Person>;
    readAll(limit: number, offset: number): Promise<Person[]>;
    searchByFilter(filters: PersonFilter, limit: number): Promise<Person[]>;
    searchByVector(vector: number[], topK: number): Promise<Person[]>;
}
