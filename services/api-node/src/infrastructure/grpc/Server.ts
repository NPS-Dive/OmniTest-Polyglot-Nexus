/**
 * @file Server.ts
 * @description Infrastructure layer for handling gRPC server initialization and transport.
 * Obeys SRP: Only handles network/transport layer logic.
 */

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import { fileURLToPath } from 'url';
import path from 'path';

// Recreate __dirname for ESM context
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class GrpcServer {
    private server: grpc.Server;
    private port: string | number;

    /**
     * @param port The port number where the gRPC server will listen
     */
    constructor(port: string | number) {
        this.server = new grpc.Server();
        this.port = port;
    }

    /**
     * Binds the PersonService controller to the gRPC server.
     * @param personController The presentation controller handling gRPC requests.
     */
    public bindPersonService(personController: any): void {
        // 1. Resolve the path to the shared proto file. 
        // Relative from: src/infrastructure/grpc/Server.ts -> ../../../shared/proto/person_service.proto
        const PROTO_PATH = path.resolve(__dirname, '../../../../../shared/proto/person_service.proto');
        
        // 2. Load the proto file synchronously
        const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
            keepCase: true,
            longs: String,
            enums: String,
            defaults: true,
            oneofs: true,
        });

        // 3. Load the package definition into a gRPC object
        const protoDescriptor = grpc.loadPackageDefinition(packageDefinition) as any;
        
        // 4. Extract the correct namespace matching the .proto file
        const personProto = protoDescriptor.omnitest.polyglot.nexus;

        // 5. Bind the service methods to the controller implementation
        this.server.addService(personProto.PersonService.service, {
            CreatePerson: personController.createPerson.bind(personController),
            ReadAllPersons: personController.readAllPersons.bind(personController),
            SearchByFilter: personController.searchByFilter.bind(personController),
            SearchByVector: personController.searchByVector.bind(personController),
        });
    }

    /**
     * Starts the gRPC server listening on the specified port.
     */
    public start(): void {
        this.server.bindAsync(
            `0.0.0.0:${this.port}`,
            grpc.ServerCredentials.createInsecure(), // Development only; use TLS in prod
            (error, boundPort) => {
                if (error) {
                    console.error(`[gRPC] Server binding failed: ${error.message}`);
                    return;
                }
                console.log(`[gRPC] Server is running on port ${boundPort}`);
            }
        );
    }
}
