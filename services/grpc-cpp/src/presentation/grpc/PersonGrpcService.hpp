// ============================================================================
// File: src/presentation/grpc/PersonGrpcService.hpp
// Purpose: gRPC adapter — proto messages <-> domain::Person. No SQL here.
// SOLID role: SRP (mapping + RPC dispatch). DIP (depends on IPersonRepository).
// Namespace: omnitest::polyglot::nexus — matches package in person_service.proto.
// Generated headers: person_service.pb.h / person_service.grpc.pb.h (not person::v1).
// ============================================================================

#pragma once

#include "person_service.grpc.pb.h"

#include "../../domain/IPersonRepository.hpp"

#include <memory>

namespace omnitest {
namespace polyglot {
namespace nexus {

/**
 * @class PersonGrpcService
 * @brief Implements PersonService (Create, ReadAll, SearchByFilter, SearchByVector).
 *
 * Translates proto field names to domain/SQL names:
 *   gender <-> sex, job_category <-> occupation, embedding_vector <-> embedding.
 * birth_date is derived as (current_year - age)-01-01 and is never persisted.
 */
class PersonGrpcService final : public PersonService::Service {
public:
    /**
     * @brief Inject the repository. Ownership is shared so tests can stub it.
     */
    explicit PersonGrpcService(std::shared_ptr<domain::IPersonRepository> repository);

    /**
     * @brief Persist one Person and fill success / message / inserted_id.
     */
    grpc::Status CreatePerson(grpc::ServerContext* context,
                              const CreatePersonRequest* request,
                              CreatePersonResponse* response) override;

    /**
     * @brief Paginated list. limit default 50 max 500; total_count is table size.
     */
    grpc::Status ReadAllPersons(grpc::ServerContext* context,
                                const ReadAllPersonsRequest* request,
                                PersonListResponse* response) override;

    /**
     * @brief Filter by first_name, last_name, min_age, max_age, gender, national_code.
     */
    grpc::Status SearchByFilter(grpc::ServerContext* context,
                                const FilterSearchRequest* request,
                                PersonListResponse* response) override;

    /**
     * @brief L2 vector search. top_k default 10 max 100.
     */
    grpc::Status SearchByVector(grpc::ServerContext* context,
                                const VectorSearchRequest* request,
                                PersonListResponse* response) override;

private:
    std::shared_ptr<domain::IPersonRepository> repository_;
};

}  // namespace nexus
}  // namespace polyglot
}  // namespace omnitest
