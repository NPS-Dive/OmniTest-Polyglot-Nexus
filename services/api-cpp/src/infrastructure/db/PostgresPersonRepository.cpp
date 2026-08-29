// ============================================================================
// File: src/infrastructure/db/PostgresPersonRepository.cpp
// Purpose: All SQL for persons_cpp — Create, ReadAll, SearchByFilter, SearchByVector.
// SOLID role: infrastructure adapter. No proto types, no gRPC Status.
// Dependencies: libpqxx, pgvector (`vector` type and L2 operator <->).
// ============================================================================

#include "PostgresPersonRepository.hpp"

#include <pqxx/pqxx>

#include <sstream>
#include <stdexcept>
#include <utility>

namespace infrastructure {
namespace db {
namespace {

/// SELECT list shared by every read path so row mapping stays one function.
constexpr const char* kPersonColumns =
    "id, first_name, last_name, age, sex, marital_status, children_count, "
    "living_place, occupation, national_code, embedding, has_passport";

/**
 * @brief Clamp ReadAll / filter page size: default 50, max 500.
 */
int ClampLimit(int limit) {
    if (limit <= 0) {
        return 50;
    }
    if (limit > 500) {
        return 500;
    }
    return limit;
}

/**
 * @brief Clamp SearchByVector top_k: default 10, max 100.
 */
int ClampTopK(int top_k) {
    if (top_k <= 0) {
        return 10;
    }
    if (top_k > 100) {
        return 100;
    }
    return top_k;
}

/**
 * @brief Reject negative OFFSET (Postgres would error).
 */
int ClampOffset(int offset) {
    return offset < 0 ? 0 : offset;
}

/**
 * @brief Encode a float array as a pgvector literal: [0.1,0.2,...].
 */
std::string FormatPgVector(const std::vector<float>& values) {
    std::ostringstream os;
    os << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            os << ',';
        }
        os << values[i];
    }
    os << ']';
    return os.str();
}

/**
 * @brief Parse pgvector / array text (`[1,2]` or `{1,2}`) into floats.
 */
std::vector<float> ParsePgVector(const std::string& literal) {
    std::vector<float> out;
    if (literal.empty()) {
        return out;
    }

    std::string body = literal;
    if (body.front() == '[' || body.front() == '{') {
        body.erase(body.begin());
    }
    if (!body.empty() && (body.back() == ']' || body.back() == '}')) {
        body.pop_back();
    }
    if (body.empty()) {
        return out;
    }

    std::stringstream ss(body);
    std::string token;
    while (std::getline(ss, token, ',')) {
        if (token.empty()) {
            continue;
        }
        out.push_back(std::stof(token));
    }
    return out;
}

/**
 * @brief Map one persons_cpp row onto a domain::Person (column names, not ordinals).
 */
domain::Person MapRow(const pqxx::row& row) {
    domain::Person person;
    person.id = row["id"].as<std::string>();
    person.first_name = row["first_name"].as<std::string>();
    person.last_name = row["last_name"].as<std::string>();
    person.age = row["age"].as<int>();
    person.sex = row["sex"].as<std::string>();
    person.marital_status = row["marital_status"].as<std::string>();
    person.children_count = row["children_count"].as<int>();
    person.living_place = row["living_place"].as<std::string>();
    person.occupation = row["occupation"].as<std::string>();
    person.national_code = row["national_code"].as<std::string>();

    if (!row["embedding"].is_null()) {
        person.embedding = ParsePgVector(row["embedding"].as<std::string>());
    }

    if (!row["has_passport"].is_null()) {
        person.has_passport = row["has_passport"].as<bool>();
    }

    return person;
}

/**
 * @brief SQL fragment that compares sex ignoring case, spaces, hyphens, and SEX_ prefix.
 *
 * Seed CSV stores "male" / "not specified"; Create may store "MALE" / "UNSPECIFIED".
 * @p quoted_token must already be txn.quote()'d (injection-safe).
 */
std::string SexMatchClause(const std::string& quoted_token) {
    return " AND regexp_replace("
           "upper(replace(replace(btrim(sex), '-', '_'), ' ', '_')), "
           "'^(SEX_)', '') = " +
           quoted_token;
}

}  // namespace

/**
 * @brief Remember the connection string; no network I/O until a method runs.
 */
PostgresPersonRepository::PostgresPersonRepository(std::string connection_string)
    : connection_string_(std::move(connection_string)) {}

/**
 * @brief INSERT persons_cpp. Empty id uses gen_random_uuid(); empty embedding is NULL.
 */
std::string PostgresPersonRepository::Create(const domain::Person& person) {
    try {
        pqxx::connection conn(connection_string_);
        pqxx::work txn(conn);

        const bool has_id = !person.id.empty();
        const bool has_embedding = !person.embedding.empty();

        // Two SQL shapes keep parameter indices simple (avoid binding unused UUID/vector).
        if (has_id && has_embedding) {
            const auto row = txn.exec_params(
                "INSERT INTO persons_cpp ("
                "id, first_name, last_name, age, sex, marital_status, children_count, "
                "living_place, occupation, national_code, embedding, has_passport"
                ") VALUES ("
                "$1::uuid, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::vector, $12"
                ") RETURNING id",
                person.id,
                person.first_name,
                person.last_name,
                person.age,
                person.sex,
                person.marital_status,
                person.children_count,
                person.living_place,
                person.occupation,
                person.national_code,
                FormatPgVector(person.embedding),
                person.has_passport);
            txn.commit();
            return row[0][0].as<std::string>();
        }

        if (has_id && !has_embedding) {
            const auto row = txn.exec_params(
                "INSERT INTO persons_cpp ("
                "id, first_name, last_name, age, sex, marital_status, children_count, "
                "living_place, occupation, national_code, embedding, has_passport"
                ") VALUES ("
                "$1::uuid, $2, $3, $4, $5, $6, $7, $8, $9, $10, NULL, $11"
                ") RETURNING id",
                person.id,
                person.first_name,
                person.last_name,
                person.age,
                person.sex,
                person.marital_status,
                person.children_count,
                person.living_place,
                person.occupation,
                person.national_code,
                person.has_passport);
            txn.commit();
            return row[0][0].as<std::string>();
        }

        if (!has_id && has_embedding) {
            const auto row = txn.exec_params(
                "INSERT INTO persons_cpp ("
                "id, first_name, last_name, age, sex, marital_status, children_count, "
                "living_place, occupation, national_code, embedding, has_passport"
                ") VALUES ("
                "gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, $10::vector, $11"
                ") RETURNING id",
                person.first_name,
                person.last_name,
                person.age,
                person.sex,
                person.marital_status,
                person.children_count,
                person.living_place,
                person.occupation,
                person.national_code,
                FormatPgVector(person.embedding),
                person.has_passport);
            txn.commit();
            return row[0][0].as<std::string>();
        }

        const auto row = txn.exec_params(
            "INSERT INTO persons_cpp ("
            "id, first_name, last_name, age, sex, marital_status, children_count, "
            "living_place, occupation, national_code, embedding, has_passport"
            ") VALUES ("
            "gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, $9, NULL, $10"
            ") RETURNING id",
            person.first_name,
            person.last_name,
            person.age,
            person.sex,
            person.marital_status,
            person.children_count,
            person.living_place,
            person.occupation,
            person.national_code,
            person.has_passport);
        txn.commit();
        return row[0][0].as<std::string>();
    } catch (const std::exception& ex) {
        throw std::runtime_error(std::string("Create persons_cpp failed: ") + ex.what());
    }
}

/**
 * @brief COUNT(*) then SELECT … ORDER BY id LIMIT/OFFSET on persons_cpp.
 */
std::vector<domain::Person> PostgresPersonRepository::ReadAll(int limit, int offset,
                                                             int& total) {
    limit = ClampLimit(limit);
    offset = ClampOffset(offset);

    try {
        pqxx::connection conn(connection_string_);
        pqxx::work txn(conn);

        const auto count_row = txn.exec("SELECT COUNT(*) FROM persons_cpp");
        total = count_row[0][0].as<int>();

        const auto result = txn.exec_params(
            std::string("SELECT ") + kPersonColumns +
                " FROM persons_cpp ORDER BY id LIMIT $1 OFFSET $2",
            limit,
            offset);

        std::vector<domain::Person> persons;
        persons.reserve(result.size());
        for (const auto& row : result) {
            persons.push_back(MapRow(row));
        }

        txn.commit();
        return persons;
    } catch (const std::exception& ex) {
        throw std::runtime_error(std::string("ReadAll persons_cpp failed: ") + ex.what());
    }
}

/**
 * @brief Build a parameterized WHERE from the filter; cap returned rows at 500.
 *
 * FilterSearchRequest has no limit field, so we apply the pagination max (500)
 * and still return the un-capped match count in @p total.
 */
std::vector<domain::Person> PostgresPersonRepository::SearchByFilter(
    const domain::PersonFilter& filter, int& total) {
    try {
        pqxx::connection conn(connection_string_);
        pqxx::work txn(conn);

        // quote() keeps filters injection-safe and works on libpqxx 6.x and 7.x
        // (pqxx::params is 7.x-only; Ubuntu 22.04 still ships 6.4).
        std::string where = " WHERE 1=1";

        if (filter.first_name && !filter.first_name->empty()) {
            where += " AND first_name ILIKE " + txn.quote("%" + *filter.first_name + "%");
        }
        if (filter.last_name && !filter.last_name->empty()) {
            where += " AND last_name ILIKE " + txn.quote("%" + *filter.last_name + "%");
        }
        if (filter.min_age) {
            where += " AND age >= " + txn.quote(*filter.min_age);
        }
        if (filter.max_age) {
            where += " AND age <= " + txn.quote(*filter.max_age);
        }
        if (filter.sex && !filter.sex->empty()) {
            // UNSPECIFIED also matches seed label "not specified" after normalize.
            if (*filter.sex == "UNSPECIFIED") {
                where +=
                    " AND regexp_replace("
                    "upper(replace(replace(btrim(sex), '-', '_'), ' ', '_')), "
                    "'^(SEX_)', '') IN ('UNSPECIFIED', 'NOT_SPECIFIED', '')";
            } else {
                where += SexMatchClause(txn.quote(*filter.sex));
            }
        }
        if (filter.national_code && !filter.national_code->empty()) {
            where += " AND national_code = " + txn.quote(*filter.national_code);
        }

        const auto count_row = txn.exec("SELECT COUNT(*) FROM persons_cpp" + where);
        total = count_row[0][0].as<int>();

        const int cap = ClampLimit(500);
        const auto result = txn.exec(std::string("SELECT ") + kPersonColumns +
                                     " FROM persons_cpp" + where +
                                     " ORDER BY id LIMIT " + txn.quote(cap));

        std::vector<domain::Person> persons;
        persons.reserve(result.size());
        for (const auto& row : result) {
            persons.push_back(MapRow(row));
        }

        txn.commit();
        return persons;
    } catch (const std::exception& ex) {
        throw std::runtime_error(std::string("SearchByFilter persons_cpp failed: ") +
                                 ex.what());
    }
}

/**
 * @brief L2 nearest neighbors. Rows with NULL embedding are excluded.
 */
std::vector<domain::Person> PostgresPersonRepository::SearchByVector(
    const std::vector<float>& query, int top_k) {
    top_k = ClampTopK(top_k);

    try {
        pqxx::connection conn(connection_string_);
        pqxx::work txn(conn);

        const auto result = txn.exec_params(
            std::string("SELECT ") + kPersonColumns +
                " FROM persons_cpp"
                " WHERE embedding IS NOT NULL"
                " ORDER BY embedding <-> $1::vector"
                " LIMIT $2",
            FormatPgVector(query),
            top_k);

        std::vector<domain::Person> persons;
        persons.reserve(result.size());
        for (const auto& row : result) {
            persons.push_back(MapRow(row));
        }

        txn.commit();
        return persons;
    } catch (const std::exception& ex) {
        throw std::runtime_error(std::string("SearchByVector persons_cpp failed: ") +
                                 ex.what());
    }
}

}  // namespace db
}  // namespace infrastructure
