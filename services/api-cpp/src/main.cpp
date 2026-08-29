// ============================================================================
// File: src/main.cpp
// Purpose: Composition root for the C++ Person gRPC service. Wires env → repo
//          → PersonGrpcService → grpc::Server. No business logic, no SQL.
// SOLID role: composition only (DIP). Port 50051, table persons_cpp.
// ============================================================================

#include "infrastructure/db/PostgresPersonRepository.hpp"
#include "infrastructure/telemetry/Otel.hpp"
#include "presentation/grpc/PersonGrpcService.hpp"

#include <grpcpp/grpcpp.h>

#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>

namespace {

/**
 * @brief Read an environment variable or return the documented default.
 */
std::string EnvOr(const char* key, const char* fallback) {
    const char* value = std::getenv(key);
    if (value != nullptr && value[0] != '\0') {
        return std::string(value);
    }
    return std::string(fallback);
}

/**
 * @brief Build a libpq connection string from POSTGRES_* env vars.
 *
 * Defaults match docker-compose: localhost:5432, opn_db, opn_admin, opn_secret.
 */
std::string ConnectionStringFromEnv() {
    return "host=" + EnvOr("POSTGRES_HOST", "localhost") +
           " port=" + EnvOr("POSTGRES_PORT", "5432") +
           " dbname=" + EnvOr("POSTGRES_DB", "opn_db") +
           " user=" + EnvOr("POSTGRES_USER", "opn_admin") +
           " password=" + EnvOr("POSTGRES_PASSWORD", "opn_secret");
}

}  // namespace

/**
 * @brief Process entry: telemetry stub, repository, service, blocking gRPC server.
 */
int main(int /*argc*/, char** /*argv*/) {
    infrastructure::telemetry::Otel::Initialize();

    const std::string connection_string = ConnectionStringFromEnv();
    auto repository =
        std::make_shared<infrastructure::db::PostgresPersonRepository>(connection_string);

    omnitest::polyglot::nexus::PersonGrpcService service(repository);

    const std::string address = "0.0.0.0:50051";
    grpc::ServerBuilder builder;
    builder.AddListeningPort(address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    const std::unique_ptr<grpc::Server> server(builder.BuildAndStart());
    if (!server) {
        std::cerr << "Failed to bind gRPC server on " << address << std::endl;
        return 1;
    }

    std::cout << "C++ PersonService listening on " << address
              << " (table persons_cpp)" << std::endl;
    server->Wait();
    return 0;
}
