// ============================================================================
// File: src/presentation/PersonController.ts
// Purpose: Handles incoming gRPC requests and delegates to the repository.
// SOLID Principle: Single Responsibility Principle (SRP). Only handles gRPC 
// translation (parsing requests, formatting responses). No SQL or business logic.
// ============================================================================

import * as grpc from '@grpc/grpc-js';
import { IPersonRepository } from '../domain/IPersonRepository.js';

export class PersonController {
    private repository: IPersonRepository;

    // Constructor Injection (DIP)
    constructor(repository: IPersonRepository) {
        this.repository = repository;
    }

    // Maps to rpc ReadAllPersons(ReadAllPersonsRequest) returns (PersonListResponse)
    public readAllPersons = async (
        call: grpc.ServerUnaryCall<any, any>, 
        callback: grpc.sendUnaryData<any>
    ) => {
        try {
            const limit = call.request.limit || 100;
            const offset = call.request.offset || 0;

            const result = await this.repository.readAllPersons(limit, offset);

            // Respond successfully using the gRPC callback
            callback(null, {
                persons: result.persons,
                total_count: result.totalCount
            });
        } catch (error: any) {
            console.error("[readAllPersons] Error:", error);
            callback({
                code: grpc.status.INTERNAL,
                message: "Internal server error during data retrieval."
            });
        }
    }

    // Maps to rpc SearchByVector(VectorSearchRequest) returns (PersonListResponse)
    public searchByVector = async (
        call: grpc.ServerUnaryCall<any, any>, 
        callback: grpc.sendUnaryData<any>
    ) => {
        try {
            const vector = call.request.vector || [];
            const topK = call.request.top_k || 10;

            if (vector.length !== 384) {
                return callback({
                    code: grpc.status.INVALID_ARGUMENT,
                    message: "Vector dimension mismatch. Expected 384."
                });
            }

            const result = await this.repository.searchByVector(vector, topK);

            callback(null, {
                persons: result.persons,
                total_count: result.totalCount
            });
        } catch (error: any) {
            console.error("[searchByVector] Error:", error);
            callback({ code: grpc.status.INTERNAL, message: error.message });
        }
    }
    
    // getHandlers returns the map of methods needed by grpc.Server.addService
    public getHandlers() {
        return {
            ReadAllPersons: this.readAllPersons,
            SearchByVector: this.searchByVector
            // CreatePerson and SearchByFilter would be added here
        };
    }
}
