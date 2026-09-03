// ============================================================================
// File: src/presentation/grpc/PersonGrpcService.cpp
// Purpose: Map omnitest.polyglot.nexus proto types to domain and back.
// SOLID role: presentation only — no connection strings, no SQL.
// Seed labels are lowercase ("male", "single parent", "full-time"); we
// uppercase and turn spaces/hyphens into underscores before enum lookup.
// ============================================================================

#include "PersonGrpcService.hpp"
#include "infrastructure/telemetry/Otel.hpp"

#include <algorithm>
#include <cctype>
#include <ctime>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace omnitest {
namespace polyglot {
namespace nexus {
namespace {

/**
 * @brief Trim, lowercase, and replace space/hyphen with underscore.
 *
 * "full-time" -> full_time, "single parent" -> single_parent, "MALE" -> male.
 */
std::string NormalizeToken(std::string value) {
    auto is_not_space = [](unsigned char ch) { return !std::isspace(ch); };
    value.erase(value.begin(), std::find_if(value.begin(), value.end(), is_not_space));
    value.erase(std::find_if(value.rbegin(), value.rend(), is_not_space).base(), value.end());

    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        if (ch == '-' || ch == ' ') {
            return static_cast<char>('_');
        }
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

/**
 * @brief Drop a leading enum prefix after NormalizeToken (sex_, marital_status_, …).
 */
std::string StripPrefix(const std::string& token, const std::string& prefix) {
    if (token.size() >= prefix.size() && token.compare(0, prefix.size(), prefix) == 0) {
        return token.substr(prefix.size());
    }
    return token;
}

/**
 * @brief Current civil year (local time) for birth_date derivation.
 */
int CurrentYear() {
    const std::time_t now = std::time(nullptr);
    std::tm local{};
#ifdef _WIN32
    localtime_s(&local, &now);
#else
    localtime_r(&now, &local);
#endif
    return local.tm_year + 1900;
}

/**
 * @brief Approximate ISO date: (current_year - age)-01-01. Not stored in SQL.
 */
std::string BirthDateFromAge(int age) {
    int year = CurrentYear() - age;
    if (year < 1) {
        year = 1;
    }
    std::ostringstream os;
    os << year << "-01-01";
    return os.str();
}

/**
 * @brief Map stored sex (seed or proto-style) onto proto Sex.
 */
Sex SexFromDb(const std::string& raw) {
    const std::string token = StripPrefix(NormalizeToken(raw), "sex_");
    if (token == "male") {
        return SEX_MALE;
    }
    if (token == "female") {
        return SEX_FEMALE;
    }
    if (token == "bigender") {
        return SEX_BIGENDER;
    }
    if (token == "agender") {
        return SEX_AGENDER;
    }
    return SEX_UNSPECIFIED;
}

/**
 * @brief Persist Sex as a seed label ("male") so C++ rows match the other five languages.
 */
std::string SexToDb(Sex value) {
    switch (value) {
        case SEX_MALE:
            return "male";
        case SEX_FEMALE:
            return "female";
        case SEX_BIGENDER:
            return "bigender";
        case SEX_AGENDER:
            return "agender";
        default:
            return "not specified";
    }
}

/**
 * @brief Map stored marital_status onto proto MaritalStatus.
 */
MaritalStatus MaritalFromDb(const std::string& raw) {
    const std::string token = StripPrefix(NormalizeToken(raw), "marital_status_");
    if (token == "single") {
        return MARITAL_STATUS_SINGLE;
    }
    if (token == "married") {
        return MARITAL_STATUS_MARRIED;
    }
    if (token == "divorced") {
        return MARITAL_STATUS_DIVORCED;
    }
    if (token == "widowed") {
        return MARITAL_STATUS_WIDOWED;
    }
    if (token == "single_parent") {
        return MARITAL_STATUS_SINGLE_PARENT;
    }
    return MARITAL_STATUS_UNSPECIFIED;
}

/**
 * @brief Persist MaritalStatus as a seed label ("single parent").
 */
std::string MaritalToDb(MaritalStatus value) {
    switch (value) {
        case MARITAL_STATUS_SINGLE:
            return "single";
        case MARITAL_STATUS_MARRIED:
            return "married";
        case MARITAL_STATUS_DIVORCED:
            return "divorced";
        case MARITAL_STATUS_WIDOWED:
            return "widowed";
        case MARITAL_STATUS_SINGLE_PARENT:
            return "single parent";
        default:
            return "unspecified";
    }
}

/**
 * @brief Map stored living_place onto proto LivingPlace.
 */
LivingPlace LivingFromDb(const std::string& raw) {
    const std::string token = StripPrefix(NormalizeToken(raw), "living_place_");
    if (token == "studio") {
        return LIVING_PLACE_STUDIO;
    }
    if (token == "apartment") {
        return LIVING_PLACE_APARTMENT;
    }
    if (token == "house") {
        return LIVING_PLACE_HOUSE;
    }
    if (token == "villa") {
        return LIVING_PLACE_VILLA;
    }
    if (token == "hostel") {
        return LIVING_PLACE_HOSTEL;
    }
    if (token == "dorm") {
        return LIVING_PLACE_DORM;
    }
    if (token == "hotel") {
        return LIVING_PLACE_HOTEL;
    }
    return LIVING_PLACE_UNSPECIFIED;
}

/**
 * @brief Persist LivingPlace as a seed label ("apartment").
 */
std::string LivingToDb(LivingPlace value) {
    switch (value) {
        case LIVING_PLACE_STUDIO:
            return "studio";
        case LIVING_PLACE_APARTMENT:
            return "apartment";
        case LIVING_PLACE_HOUSE:
            return "house";
        case LIVING_PLACE_VILLA:
            return "villa";
        case LIVING_PLACE_HOSTEL:
            return "hostel";
        case LIVING_PLACE_DORM:
            return "dorm";
        case LIVING_PLACE_HOTEL:
            return "hotel";
        default:
            return "unspecified";
    }
}

/**
 * @brief Map stored occupation onto proto Occupation (job_category on the wire).
 */
Occupation OccupationFromDb(const std::string& raw) {
    const std::string token = StripPrefix(NormalizeToken(raw), "occupation_");
    if (token == "job_seeker") {
        return OCCUPATION_JOB_SEEKER;
    }
    if (token == "jobless") {
        return OCCUPATION_JOBLESS;
    }
    if (token == "full_time") {
        return OCCUPATION_FULL_TIME;
    }
    if (token == "part_time") {
        return OCCUPATION_PART_TIME;
    }
    if (token == "student") {
        return OCCUPATION_STUDENT;
    }
    if (token == "housekeeper") {
        return OCCUPATION_HOUSEKEEPER;
    }
    return OCCUPATION_UNSPECIFIED;
}

/**
 * @brief Persist Occupation as a seed label ("full-time", "job seeker").
 */
std::string OccupationToDb(Occupation value) {
    switch (value) {
        case OCCUPATION_JOB_SEEKER:
            return "job seeker";
        case OCCUPATION_JOBLESS:
            return "jobless";
        case OCCUPATION_FULL_TIME:
            return "full-time";
        case OCCUPATION_PART_TIME:
            return "part-time";
        case OCCUPATION_STUDENT:
            return "student";
        case OCCUPATION_HOUSEKEEPER:
            return "housekeeper";
        default:
            return "unspecified";
    }
}

/**
 * @brief Domain -> proto. Applies gender/job_category/embedding_vector/birth_date mapping.
 */
void FillProtoPerson(const domain::Person& src, Person* dest) {
    dest->set_id(src.id);
    dest->set_first_name(src.first_name);
    dest->set_last_name(src.last_name);
    dest->set_age(src.age);
    dest->set_birth_date(BirthDateFromAge(src.age));
    dest->set_gender(SexFromDb(src.sex));
    dest->set_marital_status(MaritalFromDb(src.marital_status));
    dest->set_children_count(src.children_count);
    dest->set_living_place(LivingFromDb(src.living_place));
    dest->set_job_category(OccupationFromDb(src.occupation));
    dest->set_national_code(src.national_code);
    dest->set_has_passport(src.has_passport);
    dest->clear_embedding_vector();
    for (float value : src.embedding) {
        dest->add_embedding_vector(value);
    }
}

/**
 * @brief Proto -> domain. Inverse of FillProtoPerson; birth_date is ignored.
 */
domain::Person ToDomainPerson(const Person& src) {
    domain::Person dest;
    dest.id = src.id();
    dest.first_name = src.first_name();
    dest.last_name = src.last_name();
    dest.age = src.age();
    dest.sex = SexToDb(src.gender());
    dest.marital_status = MaritalToDb(src.marital_status());
    dest.children_count = src.children_count();
    dest.living_place = LivingToDb(src.living_place());
    dest.occupation = OccupationToDb(src.job_category());
    dest.national_code = src.national_code();
    dest.has_passport = src.has_passport();
    dest.embedding.assign(src.embedding_vector().begin(), src.embedding_vector().end());
    return dest;
}

/**
 * @brief Copy a domain page into PersonListResponse (persons + total_count).
 */
void FillList(const std::vector<domain::Person>& persons, int total,
              PersonListResponse* response) {
    response->clear_persons();
    for (const auto& person : persons) {
        FillProtoPerson(person, response->add_persons());
    }
    response->set_total_count(total);
}

}  // namespace

/**
 * @brief Keep the repository pointer; RPC methods are thin wrappers around it.
 */
PersonGrpcService::PersonGrpcService(std::shared_ptr<domain::IPersonRepository> repository)
    : repository_(std::move(repository)) {}

/**
 * @brief CreatePerson — validate nested Person, insert, return inserted_id.
 */
grpc::Status PersonGrpcService::CreatePerson(grpc::ServerContext* /*context*/,
                                             const CreatePersonRequest* request,
                                             CreatePersonResponse* response) {
    infrastructure::telemetry::RpcTimer timer;
    if (request == nullptr || !request->has_person()) {
        response->set_success(false);
        response->set_message("CreatePersonRequest.person is required");
        return grpc::Status::OK;
    }

    try {
        const std::string inserted_id = repository_->Create(ToDomainPerson(request->person()));
        response->set_success(true);
        response->set_message("Person inserted into persons_cpp");
        response->set_inserted_id(inserted_id);
        return grpc::Status::OK;
    } catch (const std::exception& ex) {
        response->set_success(false);
        response->set_message(ex.what());
        return grpc::Status::OK;
    }
}

/**
 * @brief ReadAllPersons — clamp pagination in the repository; map every row.
 */
grpc::Status PersonGrpcService::ReadAllPersons(grpc::ServerContext* /*context*/,
                                               const ReadAllPersonsRequest* request,
                                               PersonListResponse* response) {
    infrastructure::telemetry::RpcTimer timer;
    try {
        int total = 0;
        const int limit = request != nullptr ? request->limit() : 0;
        const int offset = request != nullptr ? request->offset() : 0;
        const auto persons = repository_->ReadAll(limit, offset, total);
        FillList(persons, total, response);
        return grpc::Status::OK;
    } catch (const std::exception& ex) {
        return grpc::Status(grpc::StatusCode::INTERNAL, ex.what());
    }
}

/**
 * @brief SearchByFilter — only proto optional fields that are set become constraints.
 */
grpc::Status PersonGrpcService::SearchByFilter(grpc::ServerContext* /*context*/,
                                               const FilterSearchRequest* request,
                                               PersonListResponse* response) {
    infrastructure::telemetry::RpcTimer timer;
    try {
        domain::PersonFilter filter;
        if (request != nullptr) {
            if (request->has_first_name() && !request->first_name().empty()) {
                filter.first_name = request->first_name();
            }
            if (request->has_last_name() && !request->last_name().empty()) {
                filter.last_name = request->last_name();
            }
            if (request->has_min_age()) {
                filter.min_age = request->min_age();
            }
            if (request->has_max_age()) {
                filter.max_age = request->max_age();
            }
            if (request->has_gender()) {
                // Store prefix-stripped token so SQL can match seed + proto spellings.
                filter.sex = SexToDb(request->gender());
            }
            if (request->has_national_code() && !request->national_code().empty()) {
                filter.national_code = request->national_code();
            }
        }

        int total = 0;
        const auto persons = repository_->SearchByFilter(filter, total);
        FillList(persons, total, response);
        return grpc::Status::OK;
    } catch (const std::exception& ex) {
        return grpc::Status(grpc::StatusCode::INTERNAL, ex.what());
    }
}

/**
 * @brief SearchByVector — reject an empty query vector; otherwise L2 top_k.
 */
grpc::Status PersonGrpcService::SearchByVector(grpc::ServerContext* /*context*/,
                                               const VectorSearchRequest* request,
                                               PersonListResponse* response) {
    infrastructure::telemetry::RpcTimer timer;
    if (request == nullptr || request->vector_size() == 0) {
        return grpc::Status(grpc::StatusCode::INVALID_ARGUMENT,
                            "VectorSearchRequest.vector must not be empty");
    }

    try {
        std::vector<float> query(request->vector().begin(), request->vector().end());
        const auto persons = repository_->SearchByVector(query, request->top_k());
        FillList(persons, static_cast<int>(persons.size()), response);
        return grpc::Status::OK;
    } catch (const std::exception& ex) {
        return grpc::Status(grpc::StatusCode::INTERNAL, ex.what());
    }
}

}  // namespace nexus
}  // namespace polyglot
}  // namespace omnitest
