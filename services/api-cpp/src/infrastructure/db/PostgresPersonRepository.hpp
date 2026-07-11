#pragma once
#include "../../domain/IPersonRepository.hpp"
#include <pqxx/pqxx>
#include <memory>
#include <string>

namespace infrastructure {
namespace db {

/**
 * @class PostgresPersonRepository
 * @brief PostgreSQL implementation of IPersonRepository.
 * 
 * Open/Closed Principle (OCP): We can add new DB implementations (e.g., MongoDbRepository)
 * without changing the domain or presentation layers.
 */
class PostgresPersonRepository : public domain::IPersonRepository {
private:
    std::string connection_string_;

public:
    // Constructor injects the connection string for the isolated 'persons_cpp' DB
    explicit PostgresPersonRepository(const std::string& connection_string);

    std::vector<domain::Person> ReadAllPersons(int limit, int offset) override;
    std::optional<domain::Person> GetPersonById(const std::string& id) override;
};

} // namespace db
} // namespace infrastructure
