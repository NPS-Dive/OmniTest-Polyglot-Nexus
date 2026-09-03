/**
 * @file services/grpc-node/src/infrastructure/grpc/Server.ts
 * @description Load shared proto and bind PersonService. Port 5079.
 * SOLID: SRP — transport only. Handlers live in presentation/PersonController.
 */

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import { fileURLToPath } from 'url';
import path from 'path';
import { PersonController } from '../../presentation/PersonController.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** Nested proto package after loadPackageDefinition (keepCase). */
interface PersonProtoPackage {
    omnitest: {
        polyglot: {
            nexus: {
                PersonService: {
                    service: grpc.ServiceDefinition;
                };
            };
        };
    };
}

export class GrpcServer {
    private readonly server: grpc.Server;
    private readonly port: string | number;

    constructor(port: string | number) {
        this.server = new grpc.Server();
        this.port = port;
    }

    /**
     * Binds the typed PersonController to generated PersonService methods.
     * Why keepCase: wire names stay first_name / inserted_id / top_k.
     */
    public bindPersonService(personController: PersonController): void {
        const PROTO_PATH = path.resolve(__dirname, '../../../../../shared/proto/person_service.proto');
        const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
            keepCase: true,
            longs: String,
            enums: String,
            defaults: true,
            oneofs: true,
        });

        const protoDescriptor = grpc.loadPackageDefinition(packageDefinition) as unknown as PersonProtoPackage;
        const personProto = protoDescriptor.omnitest.polyglot.nexus;

        this.server.addService(personProto.PersonService.service, {
            CreatePerson: personController.createPerson.bind(personController),
            ReadAllPersons: personController.readAllPersons.bind(personController),
            SearchByFilter: personController.searchByFilter.bind(personController),
            SearchByVector: personController.searchByVector.bind(personController),
        });
    }

    public start(): void {
        this.server.bindAsync(
            `0.0.0.0:${this.port}`,
            grpc.ServerCredentials.createInsecure(),
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
