#pragma once
#include "Person.hpp"
#include <vector>
#include <optional>

namespace domain {

/**
 * @interface IPersonRepository
 * @brief Abstract interface for Person data access.
 * 
 * Dependency Inversion Principle (DIP): High-level modules (gRPC service) 
 * should not depend on low-level modules (PostgreSQL). Both should depend 
 * on this abstraction.
 */
class IPersonRepository {
public:
    virtual ~IPersonRepository() = default;

    // Retrieves a paginated list of persons
    virtual std::vector<Person> ReadAllPersons(int limit, int offset) = 0;
    
    // Retrieves a single person by ID
    virtual std::optional<Person> GetPersonById(const std::string& id) = 0;
};

} // namespace domain
