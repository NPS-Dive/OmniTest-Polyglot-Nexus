/**
 * @file index.ts
 * @description Composition root. Env-based Postgres + DIP wiring. Port 5079.
 */

import pg from 'pg';
import { PostgresPersonRepository } from './infrastructure/db/PostgresPersonRepository.js';
import { GrpcServer } from './infrastructure/grpc/Server.js';
import { setupTelemetry } from './infrastructure/telemetry/otel.js';
import { PersonController } from './presentation/PersonController.js';

async function bootstrap(): Promise<void> {
    await setupTelemetry('grpc-node');
    const pool = new pg.Pool({
        host: process.env.POSTGRES_HOST ?? 'localhost',
        port: Number(process.env.POSTGRES_PORT ?? 5432),
        user: process.env.POSTGRES_USER ?? 'opn_admin',
        password: process.env.POSTGRES_PASSWORD ?? 'opn_secret',
        database: process.env.POSTGRES_DB ?? 'opn_db'
    });

    try {
        const client = await pool.connect();
        client.release();
        console.log('[DB] connected (persons_node)');
    } catch (error) {
        console.error('[DB] connection failed', error);
        process.exit(1);
    }

    const repository = new PostgresPersonRepository(pool);
    const controller = new PersonController(repository);
    const port = process.env.PORT ?? 5079;
    const server = new GrpcServer(port);
    server.bindPersonService(controller);
    server.start();
}

bootstrap().catch((error) => {
    console.error('Fatal bootstrap error', error);
    process.exit(1);
});
