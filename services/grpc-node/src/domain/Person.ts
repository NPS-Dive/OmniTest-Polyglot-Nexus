/**
 * @file domain/Person.ts
 * @description Domain types. Categoricals are seed VARCHAR labels.
 * SOLID: SRP — data only.
 */

export interface Person {
    id?: string;
    firstName: string;
    lastName: string;
    age: number;
    sex: string;
    maritalStatus: string;
    childrenCount: number;
    livingPlace: string;
    occupation: string;
    nationalCode: string;
    hasPassport: boolean;
    embedding?: number[];
}

/** SearchByFilter. Undefined means unconstrained. */
export interface PersonFilter {
    firstName?: string;
    lastName?: string;
    minAge?: number;
    maxAge?: number;
    sex?: string;
    nationalCode?: string;
}
