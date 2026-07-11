#pragma once
#include <grpcpp/grpcpp.h>
#include "person.grpc.pb.h" // Generated from your shared proto file
#include "../../domain/IPersonRepository.hpp"
#include <memory>

namespace presentation {
namespace grpc_api {

/**
 * @class PersonGrpcService
 * @brief Implements the gRPC contract using the injected Domain Repository.
 * 
 * Liskov Substitution Principle (LSP): This service uses IPersonRepository. It doesn't 
 * care if the underlying DB is Postgres, Mock, or Memory. It behaves correctly regardless.
 */
class PersonGrpcService final : public person::v1::PersonService::Service {
private:
    std::shared_ptr<domain::IPersonRepository> repository_;

public:
    // Dependency Injection via constructor
    explicit PersonGrpcService(std::shared_ptr<domain::IPersonRepository> repository);

    // gRPC Method Overrides
    ::grpc::Status ReadAllPersons(::grpc::ServerContext* context, 
                                  const ::person::v1::PaginationRequest* request, 
                                  ::person::v1::PersonListResponse* response) override;
                                  
    // (Other methods like GetPerson, CreatePerson would be declared here)
};

} // namespace grpc_api
} // namespace presentation
