// ============================================================================
// File: src/domain/Person.hpp
// Purpose: Language-agnostic Person entity used by the C++ gRPC service.
// SOLID role: SRP — data only. No SQL, no protobuf, no I/O.
// Dependencies: C++ standard library. Consumed by IPersonRepository and mappers.
// Persistence mapping (Postgres persons_cpp — do not rename columns):
//   proto.gender           -> sex
//   proto.job_category     -> occupation
//   proto.embedding_vector -> embedding
//   proto.has_passport     -> has_passport
//   proto.birth_date       -> NOT stored; derived on read from age
// ============================================================================

#pragma once

#include <string>
#include <vector>

namespace domain {

/**
 * @struct Person
 * @brief Core domain record for one row in persons_cpp.
 *
 * Categorical fields stay as VARCHAR tokens so the repository can persist
 * seed labels (lowercase, spaces, hyphens) and proto-style tokens (MALE)
 * without depending on generated protobuf enums (DIP).
 */
struct Person {
    /// UUID primary key. Empty on create means the database assigns one.
    std::string id;

    std::string first_name;
    std::string last_name;

    /// Non-negative age in years. Used to derive birth_date on the wire.
    int age = 0;

    /// Column sex. Examples from seed: male, female, "not specified".
    std::string sex;

    /// Column marital_status. Examples: single, "single parent".
    std::string marital_status;

    int children_count = 0;

    /// Column living_place. Examples: house, studio, hostel.
    std::string living_place;

    /// Column occupation. Examples: student, "job seeker", "full-time".
    std::string occupation;

    std::string national_code;

    /// Column embedding (pgvector, 384 dims). Empty means SQL NULL.
    std::vector<float> embedding;

    /// Column has_passport. Seed rows default to false.
    bool has_passport = false;
};

}  // namespace domain
