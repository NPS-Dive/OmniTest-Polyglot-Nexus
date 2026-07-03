// src/infrastructure/grpc/Server.ts

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

/**
 * GrpcServer
 * 
 * Encapsulates the configuration and lifecycle of the @grpc/grpc-js server.
 */
export class GrpcServer {
    private server: grpc.Server;

    constructor() {
        this.server = new grpc.Server();
    }

    /**
     * Loads the protobuf definition and binds the controller methods to it.
     * 
     * @param controller - The initialized PersonController
     */
    public setup(controller: any): void {
        // In native ESM, __dirname does not exist. We must calculate it using import.meta.url.
        const __filename = fileURLToPath(import.meta.url);
        const __dirname = dirname(__filename);

        // Path to the shared proto file in your monorepo structure
        const PROTO_PATH = join(__dirname, '../../../../shared/proto/person.proto');

        // Load the .proto file synchronously with standard configuration
        const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
            keepCase: true,
            longs: String,
            enums: String,
            defaults: true,
            oneofs: true
        });

        // Extract the loaded package (assuming your proto package is named 'person_service')
        const protoDescriptor = grpc.loadPackageDefinition(packageDefinition) as any;
        const personProto = protoDescriptor.person_service; 

        // Bind the gRPC service definition to our controller implementation
        this.server.addService(personProto.PersonService.service, {
            SearchPersons: controller.searchPersons
        });
    }

    /**
     * Starts the gRPC server on the specified port.
     */
    public start(port: number = 5079): void {
        const address = `0.0.0.0:${port}`;
        
        this.server.bindAsync(
            address,
            grpc.ServerCredentials.createInsecure(),
            (error, boundPort) => {
                if (error) {
                    console.error(`Failed to bind server on ${address}`, error);
                    return;
                }
                // start() is deprecated in newer versions, binding automatically starts it, 
                // but we call it safely if it exists on the instance.
                this.server.start(); 
                console.log(`[api-node] gRPC Server running seamlessly at ${address}`);
            }
        );
    }
}
