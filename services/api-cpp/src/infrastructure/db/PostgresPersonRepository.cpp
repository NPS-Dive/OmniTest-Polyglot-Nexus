#include "PostgresPersonRepository.hpp"
#include <iostream>

namespace infrastructure {
namespace db {

PostgresPersonRepository::PostgresPersonRepository(const std::string& connection_string)
    : connection_string_(connection_string) {}

std::vector<domain::Person> PostgresPersonRepository::ReadAllPersons(int limit, int offset) {
    std::vector<domain::Person> persons;
    try {
        // Create a connection and transaction
        pqxx::connection C(connection_string_);
        pqxx::work W(C);

        // Safe default for pagination to prevent division by zero or massive queries
        if (limit <= 0) limit = 10;
        if (offset < 0) offset = 0;

        // Parameterized query to prevent SQL injection
        std::string sql = "SELECT id, national_id, first_name, last_name, age, gender FROM persons LIMIT $1 OFFSET $2";
        pqxx::result R = W.exec_params(sql, limit, offset);

        // Map database rows to Domain Entities
        for (auto const& row : R) {
            domain::Person p;
            p.id = row[0].c_str();
            p.national_id = row[1].c_str();
            p.first_name = row[2].c_str();
            p.last_name = row[3].c_str();
            p.age = row[4].as<int>();
            p.gender = row[5].c_str();
            persons.push_back(p);
        }
    } catch (const std::exception& e) {
        std::cerr << "DB Error in ReadAllPersons: " << e.what() << std::endl;
    }
    return persons;
}

std::optional<domain::Person> PostgresPersonRepository::GetPersonById(const std::string& id) {
    try {
        pqxx::connection C(connection_string_);
        pqxx::work W(C);

        std::string sql = "SELECT id, national_id, first_name, last_name, age, gender FROM persons WHERE id = $1";
        pqxx::result R = W.exec_params(sql, id);

        if (!R.empty()) {
            auto const& row = R[0];
            domain::Person p;
            p.id = row[0].c_str();
            p.national_id = row[1].c_str();
            p.first_name = row[2].c_str();
            p.last_name = row[3].c_str();
            p.age = row[4].as<int>();
            p.gender = row[5].c_str();
            return p;
        }
    } catch (const std::exception& e) {
        std::cerr << "DB Error in GetPersonById: " << e.what() << std::endl;
    }
    return std::nullopt;
}

} // namespace db
} // namespace infrastructure
