// ============================================================================
// File: src/domain/IPersonRepository.hpp
// Purpose: Persistence port for Person. Presentation depends on this, not pqxx.
// SOLID role: DIP + ISP — the only data-access surface the gRPC layer needs.
// Dependencies: domain::Person. Implemented by PostgresPersonRepository.
// Table contract: implementations MUST use persons_cpp only.
// ============================================================================

#pragma once

#include "Person.hpp"

#include <optional>
#include <string>
#include <vector>

namespace domain {

/**
 * @struct PersonFilter
 * @brief Optional SearchByFilter criteria from FilterSearchRequest.
 *
 * Unset optionals mean "do not constrain that column". sex is a normalized
 * proto token without prefix (MALE, FEMALE, …) or empty for unspecified.
 */
struct PersonFilter {
    std::optional<std::string> first_name;
    std::optional<std::string> last_name;
    std::optional<int> min_age;
    std::optional<int> max_age;
    /// Normalized sex token (MALE / FEMALE / BIGENDER / AGENDER / UNSPECIFIED).
    std::optional<std::string> sex;
    std::optional<std::string> national_code;
};

/**
 * @interface IPersonRepository
 * @brief Abstract Person persistence. High-level modules depend on this.
 *
 * Methods match the four proto RPCs. Pagination: limit default 50 max 500;
 * vector top_k default 10 max 100. Implementations must clamp.
 */
class IPersonRepository {
public:
    virtual ~IPersonRepository() = default;

    /**
     * @brief Insert one row into persons_cpp.
     * @param person Domain fields. Empty id triggers gen_random_uuid().
     * @return Inserted UUID as a string (CreatePersonResponse.inserted_id).
     */
    virtual std::string Create(const Person& person) = 0;

    /**
     * @brief Paginated read of persons_cpp plus a cheap COUNT(*) total.
     * @param limit Page size (clamped 1..500, default 50 when <= 0).
     * @param offset Rows to skip (clamped to >= 0).
     * @param total Out-parameter: full table row count, not page size.
     */
    virtual std::vector<Person> ReadAll(int limit, int offset, int& total) = 0;

    /**
     * @brief Constrained search (names ILIKE, age range, sex, national_code).
     * @param filter Optional fields; only set members become WHERE clauses.
     * @param total Out-parameter: number of rows matching the filter.
     */
    virtual std::vector<Person> SearchByFilter(const PersonFilter& filter, int& total) = 0;

    /**
     * @brief Nearest-neighbor search with pgvector L2 operator `<->`.
     * @param query Query embedding (typically 384 floats).
     * @param top_k Result cap (clamped 1..100, default 10 when <= 0).
     */
    virtual std::vector<Person> SearchByVector(const std::vector<float>& query, int top_k) = 0;
};

}  // namespace domain
