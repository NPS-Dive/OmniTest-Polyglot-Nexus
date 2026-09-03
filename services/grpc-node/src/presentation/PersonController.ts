/**
 * @file presentation/PersonController.ts
 * @description gRPC handlers. Typed Person; full FilterSearchRequest; top_k.
 * SOLID: DIP — IPersonRepository only.
 */

import * as grpc from '@grpc/grpc-js';
import { IPersonRepository } from '../domain/IPersonRepository.js';
import { Person, PersonFilter } from '../domain/Person.js';
import {
    clampLimit,
    clampTopK,
    derivedBirthDate,
    protoEnumToSeed,
    seedToProtoEnum
} from './enumMap.js';

type UnaryCallback = (error: grpc.ServiceError | null, response?: unknown) => void;

function toProto(person: Person) {
    return {
        id: person.id ?? '',
        first_name: person.firstName,
        last_name: person.lastName,
        age: person.age,
        birth_date: derivedBirthDate(person.age),
        gender: seedToProtoEnum(person.sex, 'SEX_'),
        marital_status: seedToProtoEnum(person.maritalStatus, 'MARITAL_STATUS_'),
        children_count: person.childrenCount,
        living_place: seedToProtoEnum(person.livingPlace, 'LIVING_PLACE_'),
        job_category: seedToProtoEnum(person.occupation, 'OCCUPATION_'),
        national_code: person.nationalCode,
        has_passport: person.hasPassport,
        embedding_vector: person.embedding ?? []
    };
}

function fromProto(msg: Record<string, unknown>): Person {
    const embedding = msg.embedding_vector as number[] | undefined;
    return {
        firstName: String(msg.first_name ?? ''),
        lastName: String(msg.last_name ?? ''),
        age: Number(msg.age ?? 0),
        sex: protoEnumToSeed(String(msg.gender ?? ''), 'SEX_'),
        maritalStatus: protoEnumToSeed(String(msg.marital_status ?? ''), 'MARITAL_STATUS_'),
        childrenCount: Number(msg.children_count ?? 0),
        livingPlace: protoEnumToSeed(String(msg.living_place ?? ''), 'LIVING_PLACE_'),
        occupation: protoEnumToSeed(String(msg.job_category ?? ''), 'OCCUPATION_'),
        nationalCode: String(msg.national_code ?? ''),
        hasPassport: Boolean(msg.has_passport),
        embedding: embedding && embedding.length ? embedding : undefined
    };
}

export class PersonController {
    constructor(private readonly repository: IPersonRepository) {}

    public async createPerson(
        call: grpc.ServerUnaryCall<{ person?: Record<string, unknown> }, unknown>,
        callback: UnaryCallback
    ): Promise<void> {
        try {
            if (!call.request.person) {
                callback({ code: grpc.status.INVALID_ARGUMENT, details: 'person is required' } as grpc.ServiceError);
                return;
            }
            const created = await this.repository.create(fromProto(call.request.person));
            callback(null, {
                success: true,
                message: 'created in persons_node',
                inserted_id: created.id
            });
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            callback({ code: grpc.status.INTERNAL, details: message } as grpc.ServiceError);
        }
    }

    public async readAllPersons(
        call: grpc.ServerUnaryCall<{ limit?: number; offset?: number }, unknown>,
        callback: UnaryCallback
    ): Promise<void> {
        try {
            const page = await this.repository.readAll(
                clampLimit(Number(call.request.limit ?? 0)),
                Math.max(Number(call.request.offset ?? 0), 0)
            );
            callback(null, { persons: page.items.map(toProto), total_count: page.totalCount });
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            callback({ code: grpc.status.INTERNAL, details: message } as grpc.ServiceError);
        }
    }

    public async searchByFilter(
        call: grpc.ServerUnaryCall<Record<string, unknown>, unknown>,
        callback: UnaryCallback
    ): Promise<void> {
        try {
            const req = call.request;
            const gender = req.gender as string | undefined;
            const filters: PersonFilter = {
                firstName: (req.first_name as string) || undefined,
                lastName: (req.last_name as string) || undefined,
                minAge: req.min_age !== undefined && req.min_age !== null ? Number(req.min_age) : undefined,
                maxAge: req.max_age !== undefined && req.max_age !== null ? Number(req.max_age) : undefined,
                sex: gender && !String(gender).includes('UNSPECIFIED')
                    ? protoEnumToSeed(String(gender), 'SEX_')
                    : undefined,
                nationalCode: (req.national_code as string) || undefined
            };
            const page = await this.repository.searchByFilter(filters, 100);
            callback(null, { persons: page.items.map(toProto), total_count: page.totalCount });
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            callback({ code: grpc.status.INTERNAL, details: message } as grpc.ServiceError);
        }
    }

    public async searchByVector(
        call: grpc.ServerUnaryCall<{ vector?: number[]; top_k?: number }, unknown>,
        callback: UnaryCallback
    ): Promise<void> {
        try {
            const vector = call.request.vector ?? [];
            if (!vector.length) {
                callback({ code: grpc.status.INVALID_ARGUMENT, details: 'vector is required' } as grpc.ServiceError);
                return;
            }
            const records = await this.repository.searchByVector(vector, clampTopK(Number(call.request.top_k ?? 0)));
            callback(null, { persons: records.map(toProto), total_count: records.length });
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            callback({ code: grpc.status.INTERNAL, details: message } as grpc.ServiceError);
        }
    }
}
