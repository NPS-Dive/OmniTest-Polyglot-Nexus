// ============================================================================
// File: src/infrastructure/db/PostgresPersonRepository.hpp
// Purpose: libpqxx adapter that is the only type allowed to touch persons_cpp.
// SOLID role: OCP/LSP — swap this class for another IPersonRepository without
//             changing PersonGrpcService. SRP — SQL and row mapping only.
// Dependencies: domain::IPersonRepository, libpqxx (implementation file).
// ============================================================================

#pragma once

#include "../../domain/IPersonRepository.hpp"

#include <string>

namespace infrastructure {
namespace db {

/**
 * @class PostgresPersonRepository
 * @brief PostgreSQL + pgvector implementation bound exclusively to persons_cpp.
 *
 * Connections are opened per call so gRPC worker threads never share a
 * pqxx::connection (libpqxx connections are not thread-safe).
 */
class PostgresPersonRepository final : public domain::IPersonRepository {
public:
    /**
     * @brief Store the libpq connection string (host/port/db/user/password).
     * @param connection_string libpq keyword/value string from the composition root.
     */
    explicit PostgresPersonRepository(std::string connection_string);

    /**
     * @brief INSERT into persons_cpp and return the new UUID.
     */
    std::string Create(const domain::Person& person) override;

    /**
     * @brief SELECT page + COUNT(*) from persons_cpp.
     */
    std::vector<domain::Person> ReadAll(int limit, int offset, int& total) override;

    /**
     * @brief Dynamic WHERE on first_name, last_name, age, sex, national_code.
     */
    std::vector<domain::Person> SearchByFilter(const domain::PersonFilter& filter,
                                               int& total) override;

    /**
     * @brief ORDER BY embedding <-> query::vector LIMIT top_k (L2, not cosine).
     */
    std::vector<domain::Person> SearchByVector(const std::vector<float>& query,
                                               int top_k) override;

private:
    std::string connection_string_;
};

}  // namespace db
}  // namespace infrastructure
