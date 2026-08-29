import * as grpc from '@grpc/grpc-js';
import { IPersonRepository } from '../domain/IPersonRepository.js';

/**
 * Controller handling incoming gRPC requests for the Person service.
 * It maps gRPC requests to the domain/repository layer and maps the results back.
 */
export class PersonController {
    private repository: IPersonRepository;

    constructor(repository: IPersonRepository) {
        this.repository = repository;
        
        // Bind methods to preserve 'this' context when called by gRPC
        this.createPerson = this.createPerson.bind(this);
        this.readAllPersons = this.readAllPersons.bind(this);
        this.searchByVector = this.searchByVector.bind(this);
        this.searchByFilter = this.searchByFilter.bind(this);
    }

    public async createPerson(call: any, callback: any): Promise<void> {
        try {
            const record = await this.repository.create(call.request);
            callback(null, { 
                id: record.id, 
                message: 'Person created successfully in persons_node table.' 
            });
        } catch (error: any) {
            console.error('[gRPC] Error in createPerson:', error.message);
            callback({ code: grpc.status.INTERNAL, details: 'Internal server error.' });
        }
    }

    public async readAllPersons(call: any, callback: any): Promise<void> {
        try {
            const limit = call.request.limit || 10;
            const offset = call.request.offset || 0;
            const records = await this.repository.readAll(limit, offset);
            
            callback(null, { 
                persons: records,
                total_count: records.length 
            });
        } catch (error: any) {
            console.error('[gRPC] Error in readAllPersons:', error.message);
            callback({ code: grpc.status.INTERNAL, details: 'Internal server error.' });
        }
    }

    public async searchByVector(call: any, callback: any): Promise<void> {
        try {
            const vector = call.request.vector;
            const limit = call.request.limit || 5;
            const records = await this.repository.searchByVector(vector, limit);
            
            callback(null, { 
                persons: records,
                total_count: records.length
            });
        } catch (error: any) {
            console.error('[gRPC] Error in searchByVector:', error.message);
            callback({ code: grpc.status.INTERNAL, details: 'Internal server error.' });
        }
    }

    /**
     * Handles the SearchByFilter gRPC endpoint.
     */
    public async searchByFilter(call: any, callback: any): Promise<void> {
        try {
            // LOGGING THE RAW REQUEST: This will show us EXACTLY what keys Postman is sending!
            console.log("[gRPC] SearchByFilter Raw Request from Postman:", JSON.stringify(call.request));

            // Extract filters aggressively. Some gRPC clients send snake_case, some send camelCase.
            // We check every possible variation based on your .proto fields.
            const filters = {
                firstName: call.request.firstName || call.request.first_name || call.request.name || "",
                lastName: call.request.lastName || call.request.last_name || call.request.family || "",
                nationalCode: call.request.nationalCode || call.request.national_code || ""
            };

            console.log("[gRPC] Parsed Filters to send to DB:", filters);

            // Execute database query using the repository
            const persons = await this.repository.searchByFilter(filters);

            // Map the database output to exactly match the gRPC .proto response fields
            const grpcPersons = persons.map(p => ({
                id: p.id,
                name: p.name,         
                family: p.family,     
                age: p.age,
                sex: p.sex,
                marital_status: p.maritalStatus,
                children_count: p.childrenCount,
                living_place: p.livingPlace,
                occupation: p.occupation,
                national_code: p.nationalCode
            }));

            // Return the mapped persons array AND the calculated total_count
            callback(null, { 
                persons: grpcPersons,
                total_count: grpcPersons.length
            });
        } catch (error) {
            console.error("Error in SearchByFilter:", error);
            callback({
                code: grpc.status.INTERNAL,
                message: "Internal server error during data retrieval."
            });
        }
    }
}
