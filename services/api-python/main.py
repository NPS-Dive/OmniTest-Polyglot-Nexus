"""
Application Entry Point.
Responsible for configuring and starting the Python gRPC server.
"""
import logging
from concurrent import futures
import grpc
from grpc_reflection.v1alpha import reflection  # NEW: Import reflection

import person_service_pb2
import person_service_pb2_grpc
from servicer import PersonGrpcService

def serve():
    """
    Bootstraps and starts the Python gRPC server with Reflection enabled.
    """
    # 1. Initialize the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 2. Bind the implemented Servicer to the gRPC server
    person_service_pb2_grpc.add_PersonServiceServicer_to_server(PersonGrpcService(), server)

    # 3. Enable gRPC Reflection (Allows UI tools to automatically discover endpoints)
    SERVICE_NAMES = (
        person_service_pb2.DESCRIPTOR.services_by_name['PersonService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # 4. Specify listening port
    port = "50052"
    server.add_insecure_port(f"[::]:{port}")

    # 5. Start the server
    server.start()
    logging.info(f"Python gRPC API Server started with Reflection, listening on port {port}...")
    server.wait_for_termination()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    serve()
