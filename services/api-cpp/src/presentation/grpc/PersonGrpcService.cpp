#include "PersonGrpcService.hpp"

namespace presentation {
namespace grpc_api {

PersonGrpcService::PersonGrpcService(std::shared_ptr<domain::IPersonRepository> repository)
    : repository_(std::move(repository)) {}

::grpc::Status PersonGrpcService::ReadAllPersons(::grpc::ServerContext* context, 
                                                 const ::person::v1::PaginationRequest* request, 
                                                 ::person::v1::PersonListResponse* response) {
    try {
        int limit = request->limit();
        int offset = request->offset();

        // Enforce safe defaults as discovered during the Java implementation phase
        if (limit <= 0) limit = 10;
        
        // Fetch domain entities from the repository
        auto persons = repository_->ReadAllPersons(limit, offset);

        // Map Domain Entities to gRPC Protobuf Messages
        for (const auto& domain_person : persons) {
            auto* grpc_person = response->add_persons();
            grpc_person->set_id(domain_person.id);
            grpc_person->set_national_id(domain_person.national_id);
            grpc_person->set_first_name(domain_person.first_name);
            grpc_person->set_last_name(domain_person.last_name);
            grpc_person->set_age(domain_person.age);
            grpc_person->set_sex(domain_person.gender); // Assuming your proto uses 'sex'
        }

        return ::grpc::Status::OK;
    } catch (const std::exception& e) {
        return ::grpc::Status(::grpc::StatusCode::INTERNAL, e.what());
    }
}

} // namespace grpc_api
} // namespace presentation
