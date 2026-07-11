#include <iostream>
#include <memory>
#include <grpcpp/grpcpp.h>
#include "infrastructure/db/PostgresPersonRepository.hpp"
#include "presentation/grpc/PersonGrpcService.hpp"

/**
 * @brief Application Entry Point
 * 
 * Orchestrates the application by wiring dependencies together.
 * Connects to the isolated 'persons_cpp' database.
 */
void RunServer() {
    // 1. Configuration (In production, load this from env vars or a config file)
    std::string db_conn_str = "dbname=persons_cpp user=postgres password=secret host=localhost port=5432";
    std::string server_address("0.0.0.0:50055"); // Unique port for C++ API

    // 2. Instantiate Dependencies (Dependency Injection)
    auto repository = std::make_shared<infrastructure::db::PostgresPersonRepository>(db_conn_str);
    presentation::grpc_api::PersonGrpcService service(repository);

    // 3. Configure and Start gRPC Server
    grpc::ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    
    std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    std::cout << "C++ gRPC Server listening on " << server_address << std::endl;
    std::cout << "Connected to independent database: persons_cpp" << std::endl;

    // 4. Block until server shuts down
    server->Wait();
}

int main(int argc, char** argv) {
    RunServer();
    return 0;
}
