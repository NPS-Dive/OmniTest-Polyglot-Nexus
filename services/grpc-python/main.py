"""
File: services/grpc-python/main.py
Purpose: Composition root — telemetry, reflection, bind PersonGrpcService, port 50052.
SOLID: no business logic here.
"""

import logging
import os
import sys
from concurrent import futures
from pathlib import Path

# Allow `python main.py` from this folder to import domain/infrastructure/presentation
sys.path.insert(0, str(Path(__file__).resolve().parent))

import grpc
from grpc_reflection.v1alpha import reflection

import person_service_pb2
import person_service_pb2_grpc
from infrastructure.db.database import SessionLocal
from infrastructure.db.postgres_person_repository import PostgresPersonRepository
from infrastructure.telemetry.otel import RpcMetricsInterceptor, setup_telemetry
from presentation.grpc.person_grpc_service import PersonGrpcService


def _open_repo():
    """Unit-of-work factory: one SQLAlchemy session + repo per RPC (DIP)."""
    session = SessionLocal()
    return session, PostgresPersonRepository(session)


def serve() -> None:
    """Start insecure gRPC + reflection (Postman / grpcurl discovery)."""
    setup_telemetry("grpc-python")
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[RpcMetricsInterceptor()],
    )
    person_service_pb2_grpc.add_PersonServiceServicer_to_server(PersonGrpcService(_open_repo), server)

    service_names = (
        person_service_pb2.DESCRIPTOR.services_by_name["PersonService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    port = os.getenv("PORT", "50052")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logging.info("grpc-python listening on %s (table persons_python)", port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    serve()
