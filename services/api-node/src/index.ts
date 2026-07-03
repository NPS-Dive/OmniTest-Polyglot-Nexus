/**
 * @file index.ts
 * @description Application Entry Point (Composition Root).
 * Wires up dependencies (DIP) and starts the infrastructure components.
 */

import pg from 'pg';
import { PostgresPersonRepository } from './infrastructure/db/PostgresPersonRepository.js';
import { PersonController } from './presentation/PersonController.js';
import { GrpcServer } from './infrastructure/grpc/Server.js';

async function bootstrap() {
    console.log('Bootstrapping api-node service...');

    // 1. Initialize Database Connection (Infrastructure)
    // Connecting using the specific user/db for the Polyglot Nexus architecture
    const pool = new pg.Pool({
        host: 'localhost',
        port: 5432,
        user: 'opn_admin',
        password: 'opn_secret',
        database: 'opn_db',
    });

    // Test DB connection on startup to fail fast if disconnected
    try {
        const client = await pool.connect();
        console.log('[DB] Successfully connected to PostgreSQL.');
        client.release();
    } catch (dbError) {
        console.error('[DB] Failed to connect to PostgreSQL:', dbError);
        process.exit(1);
    }

    // 2. Dependency Injection / Instantiation
    // Inject DB pool into Repository (Data Access)
    const personRepository = new PostgresPersonRepository(pool);
    
    // Inject Repository into Controller (Presentation layer decoupled from DB)
    const personController = new PersonController(personRepository);

    // 3. Initialize and Start the gRPC Server (Transport Layer)
    const port = process.env.PORT || 5079;
    const grpcServer = new GrpcServer(port);
    
    // Bind the controller and start listening
    grpcServer.bindPersonService(personController);
    grpcServer.start();
}

// Execute the bootstrap sequence
bootstrap().catch((err) => {
    console.error('Fatal error during bootstrap:', err);
    process.exit(1);
});
