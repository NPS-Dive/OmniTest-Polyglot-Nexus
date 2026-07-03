// ============================================================================
// File: src/index.ts
// Purpose: Composition Root / Application Entry Point.
// Design Pattern: Orchestrator. Wires up dependencies (DB Pool -> Repo -> 
// Controller -> Server) ensuring other modules remain decoupled.
// ============================================================================

import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import pg from 'pg';
import path from 'path';
import { fileURLToPath } from 'url';

// ESM Local Imports (.js required)
import { PostgresPersonRepository } from './infrastructure/db/PostgresPersonRepository.js';
import { PersonController } from './presentation/PersonController.js';

// ESM Path resolution
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROTO_PATH = path.resolve(__dirname, '../../../shared/proto/person_service.proto');

async function main() {
    // 1. Initialize Infrastructure Configuration
    // Use environment variables for production, hardcoded here for local QA
    const pool = new pg.Pool({
    user: 'opn_admin',
    host: 'localhost',
    database: 'opn_db',
    password: 'opn_secret',
    port: 5432,
});

    // 2. Load Protobuf Contracts
    const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
        keepCase: true, longs: String, enums: String, defaults: true, oneofs: true
    });
    const protoDescriptor = grpc.loadPackageDefinition(packageDefinition) as any;
    const personProto = protoDescriptor.omnitest.polyglot.nexus;

    // 3. Assemble Dependency Graph (DIP & Composition Root)
    const repository = new PostgresPersonRepository(pool);
    const controller = new PersonController(repository);

    // 4. Initialize gRPC Server
    const server = new grpc.Server();
    
    // Bind the generated handlers from our controller to the gRPC service definition
    server.addService(personProto.PersonService.service, controller.getHandlers());

    // 5. Start Listening
    const port = 5079;
    server.bindAsync(`0.0.0.0:${port}`, grpc.ServerCredentials.createInsecure(), (error, boundPort) => {
        if (error) {
            console.error("Failed to bind gRPC server:", error);
            return;
        }
        console.log(`Node.js gRPC API started securely on http://0.0.0.0:${boundPort}`);
        console.log(`Architecture configured following SOLID principles.`);
    });
}

// Bootstrap application
main().catch(err => {
    console.error("Fatal exception during startup:", err);
    process.exit(1);
});
